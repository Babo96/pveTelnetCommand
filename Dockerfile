FROM python:3.11-alpine

WORKDIR /opt/app

COPY files .

RUN pip install --no-cache-dir requests

EXPOSE 11166/tcp

CMD [ "python", "./server.py" ]
