from python:3.8-slim-bullseye
WORKDIR /app

# set env variables
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .
RUN  apt update &&  apt install libpq-dev gcc  -y
RUN pip install -r requirements.txt
EXPOSE 8080
