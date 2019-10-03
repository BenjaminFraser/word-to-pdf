FROM ubuntu:17.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN apt-get install -y build-essential libssl-dev libffi-dev python-dev
RUN apt-get install -y libreoffice

RUN adduser -D wordtopdf

WORKDIR /home/wordtopdf

RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn

COPY wordtopdf wordtopdf
COPY migrations migrations
COPY wordtopdf.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV FLASK_APP wordtopdf.py

RUN chown -R wordtopdf:wordtopdf ./
USER wordtopdf

EXPOSE 5000
ENTRYPOINT ["./boot.sh"]