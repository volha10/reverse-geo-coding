FROM python:3.11

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update \
    && apt-get -y upgrade \
    && pip3 install -r requirements.txt

COPY . .
