FROM python:3.12-alpine

LABEL maintainer="https://github.com/Jer-Pha"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk-get update
RUN apk-get install -y --no-install-recommends curl

# Install Node v20
# This should be run before apk-get install nodejs
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -

RUN apk-get install -y --no-install-recommends \
    nodejs \
    default-libmysqlclient-dev

RUN mkdir -p /code

WORKDIR /code

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements

RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements/prod.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements/dev.txt

COPY . /code/

# Build JS/static assets
RUN --mount=type=cache,target=/root/.npm npm install

RUN python ./kfdb/manage.py makemigrations
RUN python ./kfdb/manage.py collectstatic --noinput --clear

# Run the container unprivileged
RUN addgroup www && useradd -g www www
RUN chown -R www:www /code
USER www

EXPOSE 8000

# Start the server
CMD ["python", "./kfdb/manage.py", "runserver", "0.0.0.0:8000"]
