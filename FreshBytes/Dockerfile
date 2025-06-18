# syntax=docker/dockerfile:1.10.0

FROM --platform=$BUILDPLATFORM python:3.10-slim AS builder
EXPOSE 8000
WORKDIR /app
#install system dependencies
RUN apk update
RUN apd add \
    pkgconfig \
    gcc \
    musl-dev \
    bash \
    mariadb-dev

#install any needed packages specified in requirements.txt
COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt

#copy the current directory contents into the container at /usr/src/app
COPY . /app
#run server
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8000"]