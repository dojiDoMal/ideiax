FROM python:3.7-alpine3.7
LABEL maintainer 'Juracy Filho <juracy at gmail.com>'

ARG VERSION=master

ENV PYTHONUNBUFFERED 1

# TODO: Clean up some dependencies
RUN apk add --no-cache \
    binutils \
    binutils-libs \
    ca-certificates \
    freetype-dev \
    gcc \
    gettext \
    gmp \
    isl \
    jpeg-dev \
    lcms2-dev \
    libatomic \
    libc-dev \
    libgcc \
    libgomp \
    libstdc++ \
    make \
    mariadb-dev \
    mpc1 \
    mpfr3 \
    musl-dev \
    nginx \
    openjpeg-dev \
    openldap-dev \
    pkgconf \
    pkgconfig \
    postgresql-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    unzip \
    wget \
    zlib-dev

COPY requirements/* /tmp/
RUN pip install -r /tmp/dev.txt
