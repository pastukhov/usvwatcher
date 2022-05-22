FROM python
WORKDIR app
RUN pip install smbus urllib3
RUN apt install systemd-sysv
COPY *py /app/
ENTRYPOINT ["/app/server.py"]
