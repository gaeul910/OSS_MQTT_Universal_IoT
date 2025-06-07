FROM python:slim

WORKDIR /app/

ARG DB_ROOT_PASSWORD="defaultpassword"

ARG APP_FILES=./app

COPY ${APP_FILES} .

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3" , "/app/main.py" ]