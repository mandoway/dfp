# https://hub.docker.com/_/alpine/
FROM alpine:edge
MAINTAINER drad <drader@adercon.com>

# NOTICE: only needed for development (bash access) only
RUN apk add --no-cache bash

# install postgresql to get pg_dumpall
RUN apk add --no-cache postgresql xz

RUN mkdir -p /opt/bin

COPY db/crontab/root /var/spool/cron/crontabs/root
COPY db/scripts/backup_database /opt/bin/
RUN chmod 755 /opt/bin/backup_database

CMD crond -l 2 -f
