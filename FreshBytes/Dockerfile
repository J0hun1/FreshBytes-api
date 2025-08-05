FROM python:3.11-slim

#prevent python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

#set the working directory in the container
WORKDIR /code

#install system dependencies (optional, e.g. for postgreSQL adapter)
#RUN apt-get update && apt-get install -y netcat gcc

#copy and install python dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# copy the current directory contents into the container at /code
COPY . /code/

#expose the port 8000 (DEFAULT DJANGO PORT)
EXPOSE 8000

#start the Gunicorn server to serve Django app
CMD ["gunicorn", "FreshBytes.wsgi:application", "--bind", "0.0.0.0:8000"]
