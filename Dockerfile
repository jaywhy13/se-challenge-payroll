FROM python:3.6-slim
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code
RUN apt-get update --fix-missing && \
    apt-get install -y git make build-essential python-dev \
    libxml2-dev libxslt1-dev libjpeg-dev libfreetype6-dev zlib1g-dev
ADD requirements.txt /code/
RUN pip install -r requirements.txt