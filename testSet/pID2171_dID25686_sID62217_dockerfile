FROM resin/rpi-raspbian:jessie

RUN apt-get update && apt-get install ntopng

ADD start /start

RUN chmod a+x /start

CMD /start
