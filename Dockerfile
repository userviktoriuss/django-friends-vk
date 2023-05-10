FROM python:3.11
ENV PYPYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /friends
COPY . /friends
RUN pip install -r requirements.txt