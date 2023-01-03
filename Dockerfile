FROM postgres:13

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres

WORKDIR /dfp

# Install dependencies
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3.9 python3-pip wget
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN wget https://github.com/hadolint/hadolint/releases/download/v1.23.0/hadolint-Linux-x86_64 \
    && mv hadolint-Linux-x86_64 /usr/bin/hadolint \
    && chmod 555 /usr/bin/hadolint


COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .
COPY patch_database.sql /docker-entrypoint-initdb.d
