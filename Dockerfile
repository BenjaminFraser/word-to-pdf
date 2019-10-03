FROM ubuntu:18.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
	apt-get -y -q install \
		libreoffice \
		libreoffice-writer \
		ure \
		libreoffice-java-common \
		libreoffice-core \
		libreoffice-common \
		openjdk-8-jre \
		fonts-opensymbol \
		hyphen-fr \
		hyphen-de \
		hyphen-en-us \
		hyphen-it \
		hyphen-ru \
		fonts-dejavu \
		fonts-dejavu-core \
		fonts-dejavu-extra \
		fonts-droid-fallback \
		fonts-dustin \
		fonts-f500 \
		fonts-fanwood \
		fonts-freefont-ttf \
		fonts-liberation \
		fonts-lmodern \
		fonts-lyx \
		fonts-sil-gentium \
		fonts-texgyre \
		python3 \
		python3-pip \
		build-essential libssl-dev libffi-dev python-dev \
		fonts-tlwg-purisa && \
	apt-get -y -q remove libreoffice-gnome && \
	apt -y autoremove && \
	rm -rf /var/lib/apt/lists/*

#RUN apt-get install -y python3 
#RUN apt-get install -y python3-pip
#RUN apt-get install -y build-essential libssl-dev libffi-dev python-dev

RUN adduser --disabled-password wordtopdf

WORKDIR /home/wordtopdf

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn pymysql

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