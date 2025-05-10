FROM python:slim

WORKDIR /app/

ARG DB_ROOT_PASSWORD="defaultpassword"

ARG APP_FILES=.

COPY ${APP_FILES} .

RUN pip3 install flask

RUN pip3 install pymysql

RUN pip3 install cryptography

ENTRYPOINT [ "python3" , "/app/main.py" ]