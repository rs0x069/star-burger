# BUILD BACKEND BASE
FROM python:3.10-alpine as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update; \
    apk add --no-cache --virtual .build-deps \
    gcc \
    libc-dev \
    # Pillow dependencies
    jpeg-dev \
    libjpeg \
    libjpeg-turbo-dev \
    zlib-dev \
    freetype-dev \
    libpng-dev; \
    rm -rf /var/cache/apk/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip;  \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r /app/requirements.txt;

# BUILD FRONTEND
FROM node:14-alpine as frontend

RUN npm install

WORKDIR /app

COPY package*.json ./
COPY bundles/ ./bundles/
COPY bundles-src/ ./bundles-src/

RUN npm ci --dev; \
    ./node_modules/.bin/parcel build ./bundles-src/index.js --dist-dir ./bundles --public-url="./"

# BUILD BACKEND DEV
FROM python:3.10-alpine as dev

ENV APP_HOME=/app/
ENV USER=starburger
ENV GROUP=starburger

RUN apk update; \
    apk add --no-cache \
    git \
    gcc \
    libc-dev \
    # Pillow dependencies
    jpeg-dev \
    libjpeg \
    libjpeg-turbo-dev \
    zlib-dev \
    freetype-dev \
    libpng-dev \
    # psycopg2 dependencies
    postgresql-dev \
    python3-dev \
    musl-dev; \
    rm -rf /var/cache/apk/*

WORKDIR $APP_HOME

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
COPY --from=frontend /app/bundles ./bundles

RUN pip install --upgrade pip; \
    pip install --no-cache /wheels/*

RUN addgroup -S $GROUP && adduser -S $USER -G $GROUP

COPY --chown=$USER:$GROUP entrypoint.sh .

USER $USER

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# BUILD BACKEND PROD
FROM python:3.10-alpine as prod

ENV APP_HOME=/app/
ENV USER=starburger
ENV GROUP=starburger

RUN apk update; \
    apk add --no-cache \
    git \
    gcc \
    libc-dev \
    # Pillow dependencies
    jpeg-dev \
    libjpeg \
    libjpeg-turbo-dev \
    zlib-dev \
    freetype-dev \
    libpng-dev \
    # psycopg2 dependencies
    postgresql-dev \
    python3-dev \
    musl-dev; \
    rm -rf /var/cache/apk/*;

WORKDIR $APP_HOME

COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
COPY --from=frontend /app/bundles ./bundles

RUN pip install --upgrade pip; \
    pip install --no-cache /wheels/*;

RUN addgroup -S $GROUP && adduser -S $USER -G $GROUP

COPY --chown=$USER:$GROUP . .
RUN chmod +x entrypoint.sh

USER $USER

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "-w", "5", "-b", "0.0.0.0:8000", "star_burger.wsgi:application"]

# Создавать релизы, например, 2015-04-06-15:42:17 или v100
# Любые изменения обязаны создавать новый релиз.
