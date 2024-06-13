FROM python:3.12-slim

LABEL maintainer="https://github.com/Jer-Pha"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y default-libmysqlclient-dev
RUN mkdir -p /code

WORKDIR /code

COPY ./requirements /requirements

RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements/prod.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements/dev.txt

COPY . /code/

RUN python ./kfdb/manage.py makemigrations

# Run the container unprivileged
RUN addgroup www && useradd -g www www
RUN chown -R www:www /code
USER www

EXPOSE 8000

# Start the server
CMD ["python", "./kfdb/manage.py", "runserver", "0.0.0.0:8000"]
