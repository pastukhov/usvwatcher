FROM python
WORKDIR app
RUN pip install smbus
COPY *py .
