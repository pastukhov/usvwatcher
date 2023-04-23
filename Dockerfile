FROM python

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install systemd-sysv -y && rm -rf /var/cache/apt

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY *py /app/

ENTRYPOINT ["/app/server.py"]
