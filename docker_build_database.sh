#!/bin/sh

docker run --name mysql -d -e MYSQL_RANDOM_ROOT_PASSWORD=yes \
-e MYSQL_DATABASE=wordtopdf -e MYSQL_USER=wordtopdf \
-e MYSQL_PASSWORD=$DATABASE_PASSWORD \
mysql/mysql-server:5.7
