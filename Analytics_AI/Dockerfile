FROM python:slim

WORKDIR /program

ARG APP_FILES=./program

COPY ${APP_FILES} .

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3" , "/program/program_start.py" ]