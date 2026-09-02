# base image
FROM python:3.10.6-slim

# setup environment variable
ENV DockerHOME=/home/app/webapp

# set work directory
RUN mkdir -p $DockerHOME

# where your code lives
WORKDIR $DockerHOME

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt -y install gettext

# install dependencies
RUN pip install --upgrade pip

COPY ./requirements.txt $DockerHOME/requirements.txt

RUN pip install -r requirements.txt --index-url=https://mirrors.aliyun.com/pypi/simple/
# copy whole project to your docker home directory.

#RUN useradd -r dev

#USER dev

WORKDIR $DockerHOME

COPY . $DockerHOME
# run this command to install all dependencies
