FROM ubuntu:17.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y build-essential libssl-dev libffi-dev python-dev
RUN apt-get install -y libreoffice

ADD app /app
WORKDIR /app

RUN pip3 install -r requirements.txt

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT ["python3"]
CMD ["app.py"]