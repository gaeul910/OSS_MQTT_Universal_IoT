FROM mysql

WORKDIR /init-db

COPY ./init-db/ .

ENV MYSQL_ROOT_PASSWORD=defaultpassword1

ENV MYSQL_DATABASE=iot-db

ADD /init-db/init-db.sh /docker-entrypoint-initdb.d