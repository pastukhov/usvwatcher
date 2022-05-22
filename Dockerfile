FROM python
WORKDIR app
RUN pip install smbus urllib3
COPY *py /app/
ENTRYPOINT ["/app/server.py"]
