import subprocess
import getopt
import http.server
import json
import posixpath
import socketserver
import sys
from threading import Thread
import threading
import time
import urllib3
import monitor

class OurHTTPServer(socketserver.ThreadingMixIn,http.server.HTTPServer):
  def __init__(self, server_address, RequestHandlerClass, monitor, bind_and_activate=True):
    http.server.HTTPServer.__init__(self,server_address,RequestHandlerClass,bind_and_activate)
    self.monitor=monitor # type: monitor.Monitor


class Handler(http.server.SimpleHTTPRequestHandler):
    @classmethod
    def getReturnData(cls, error=None, **kwargs):
        if error is not None:
            rt = {'status': error}
        else:
            rt = {'status': 'OK'}
        for k in list(kwargs.keys()):
            if kwargs[k] is not None:
                rt[k] = kwargs[k]
        return rt
    @classmethod
    def pathQueryFromUrl(cls, url):
        (path, sep, query) = url.partition('?')
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib3.parse.unquote(path))
        return (path, query)

    @classmethod
    def getRequestParam(cls,query):
        return urllib3.parse.parse_qs(query, True)
    
    def sendJsonResponse(self,data):
        r=json.dumps(data).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(r)))
        self.send_header("Last-Modified", self.date_time_string())
        self.end_headers()
        self.wfile.write(r)

    def do_GET(self):
        request=""
        values=self.server.monitor.getCurrentValues()
        self.sendJsonResponse(values.toPlain())
        return
        #self.sendJsonResponse(self.getReturnData("unknown request %s"%request))  

    def log_message(self,*args):
        pass    


def runServer(mon,port, addr="localhost"):
    server=OurHTTPServer((addr,port),Handler,mon)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()

if __name__ == '__main__':
    port=8082
    address="localhost"
    shutdownLevel=None
    try:
        optlist,args=getopt.getopt(sys.argv[1:],'p:a:s:')
    except getopt.GetoptError as err:
        print(err)
        sys.exit(1)   
    for o,a in optlist:
        if o == '-p':
            port=int(a)
        elif o == '-a':
            address=a
        elif o == '-s':
            shutdownLevel=int(a)
    print("running with port %s, address %s shutdown %s"%(port,address,shutdownLevel))            
    mon=monitor.Monitor()
    mon.startQuery()        
    runServer(mon,port,address)
    numLow=0
    while True:
        now=time.time()
        current=mon.getCurrentValues()
        if current.timestamp  < (now -120):
            print("Status not updated")
            sys.exit(1)
        if shutdownLevel is not None:
            if current.discharging and current.percent < shutdownLevel:
                numLow +=1
                if numLow > 5:
                    print("USV shutdown level reached, shutdown system")
                    subprocess.run("sudo -n halt",shell=True)
                    numLow=0
            else:
                numLow=0
        time.sleep(10)