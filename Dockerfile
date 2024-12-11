FROM python:3.9-alpine

COPY requirements.txt /opt/freshtoons/

WORKDIR /opt/freshtoons
RUN pip install -r requirements.txt

COPY src /opt/freshtoons/

entrypoint ["python3" "src/main.py"]