#!/bin/sh

docker run --name wordtopdf -d -p 8000:5000 --rm --link mysql:dbserver -e DATABASE_URL=mysql+pymysql://wordtopdf:$DATABASE_PASSWORD@dbserver/wordtopdf wordtopdf:latest
