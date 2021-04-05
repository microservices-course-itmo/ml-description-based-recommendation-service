FROM python:3.6-slim-buster

ENV PYTHONUNBUFFERED 1

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary

ENV STATIC_URL /static
ENV STATIC_PATH /static
ENV STATIC_INDEX 0

COPY swagger.json swagger.json
COPY logs.txt logs.txt
COPY . .

EXPOSE 5000
CMD ["flask", "run"]

