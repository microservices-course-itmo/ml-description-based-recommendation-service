FROM python:3.6-buster
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
RUN apt-get update -y && \
    apt-get install -y python-pip python-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary
EXPOSE 5000
ENV STATIC_URL /static
# Absolute path in where the static files wil be
ENV STATIC_PATH /static
# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured in this case it will be 0)
# ENV STATIC_INDEX 1
ENV STATIC_INDEX 0
COPY . .
CMD ["flask", "run"]

