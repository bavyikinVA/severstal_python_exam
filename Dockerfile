FROM python:3.12

RUN mkdir server

ADD main.py server/main.py

ADD requirements.txt server/requirements.txt

RUN pip install -r server/requirements.txt

CMD uvicorn main:app --host 0.0.0.0 --port 8080 
