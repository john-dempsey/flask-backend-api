FROM python:3.12.7

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install gunicorn pymysql cryptography

COPY app app
COPY migrations migrations
COPY server.py config.py boot.sh ./
RUN chmod a+x boot.sh

ENV FLASK_APP=server.py
ENV FLASK_RUN_PORT=8000

EXPOSE 8000
ENTRYPOINT ["./boot.sh"]