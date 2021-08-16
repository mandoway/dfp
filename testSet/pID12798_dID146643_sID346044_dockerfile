from ubuntu

# apt-get
RUN sudo apt-get update -y
RUN sudo apt-get install -y git wget

# memcached
RUN sudo apt-get install -y memcached

# golang
RUN wget --no-verbose https://storage.googleapis.com/golang/go1.4.2.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.4.2.linux-amd64.tar.gz

ENV GOPATH /go
ENV GOROOT /usr/local/go
ENV PATH /usr/local/go/bin:/go/bin:/usr/local/bin:$PATH

# project
RUN go get github.com/bradfitz/gomemcache/memcache
RUN go get github.com/go-sql-driver/mysql

RUN git clone https://github.com/ifapmzadu6/Hoppin-Server

EXPOSE 3306 80 443

CMD go run /Hoppin-Server/main.go

