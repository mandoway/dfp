FROM alpine:3.2

RUN apk -U add tzdata && rm -f /var/cache/apk/*
COPY mkrootfs /usr/local/sbin/mkrootfs

ENTRYPOINT ["mkrootfs"]
