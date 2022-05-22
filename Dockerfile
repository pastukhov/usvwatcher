FROM python
WORKDIR app
RUN pip install smbus urllib3
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install systemd-sysv -y && rm -rf /var/cache/apt
COPY *py /app/
ENTRYPOINT ["/app/server.py"]
