FROM python:3.12

LABEL maintainer="https://github.com/Jer-Pha"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY ./requirements /requirements

RUN pip install --upgrade pip
RUN --mount=type=cache,target=/root/.cache/pip pip install -r /requirements/prod.txt

COPY . /code/

# Run the container unprivileged
RUN addgroup www && useradd -g www www
RUN chown -R www:www /code
USER www


# Output information about the build
RUN git log -n 1 --pretty=format:"%h" > GIT_COMMIT
RUN date -u +'%Y-%m-%dT%H:%M:%SZ' > BUILD_DATE

EXPOSE 8000

# Start the server
CMD ["python", "./kfdb/manage.py", "runserver", "0.0.0.0:8000"]
