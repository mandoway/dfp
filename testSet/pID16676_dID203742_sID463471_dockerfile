FROM golang:1.6.2-wheezy 

COPY . /go/src/github.com/junhuqc/gobot
RUN apt-get update && apt-get install -y pkg-config

WORKDIR /tmp

RUN wget -q  https://download.libsodium.org/libsodium/releases/libsodium-1.0.10.tar.gz \
    && wget -q  https://download.libsodium.org/libsodium/releases/libsodium-1.0.10.tar.gz.sig \
    && wget -q  https://download.libsodium.org/jedi.gpg.asc \
    && gpg --import jedi.gpg.asc \
    && gpg --verify libsodium-1.0.10.tar.gz.sig libsodium-1.0.10.tar.gz \
    && tar zxvf libsodium-1.0.10.tar.gz \
    && cd libsodium* \
    && ./configure && make check \
    && make install \
    && ldconfig \
    && cd /tmp

RUN wget -q http://download.zeromq.org/zeromq-4.1.3.tar.gz \
    && tar zxvf zeromq-4.1.3.tar.gz \
    && cd zeromq* \
    && ./configure --with-libsodium && make && make check \
    && make install \
    && ldconfig \
    && cd /tmp

RUN wget -q http://download.zeromq.org/czmq-3.0.2.tar.gz \
    && tar zxvf czmq-3.0.2.tar.gz \
    && cd czmq* \
    && ./configure && make check \
    && make install \
    && ldconfig \
    && rm -rf /var/cache/apk/* /tmp/*

WORKDIR /go/src/github.com/junhuqc/gobot

EXPOSE 80
CMD ["tail -f /dev/null"]
