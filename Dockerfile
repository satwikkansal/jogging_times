FROM python:3.7-buster
COPY server/ ./server
COPY tests/ ./tests
COPY ./requirements.txt ./requirements.txt
COPY ./test-requirements.txt ./test-requirements.txt
COPY ./manage.py ./manage.py
COPY ./migrations ./migrations

RUN pip install -r requirements.txt

RUN pip install gunicorn[gevent]

CMD ["python", "manage.py", "create_db"]
CMD ["python", "manage.py", "db", "upgrade"]

CMD gunicorn --worker-class gevent --workers 4 server:app --bind 0.0.0.0:5000
