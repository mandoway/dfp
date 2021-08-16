# Build from PHP oficial image
FROM php:5.6

# Me!
MAINTAINER Jhon Eslava <jhonjairo048@gmail.com>

# Install Git!
RUN apt-get update && apt-get install -y git --no-install-recommends && rm -r /var/lib/apt/lists/*

# Install Phalcon Dependences!
RUN apt-get update && apt-get install -y php5-dev php5-mysql gcc libpcre3-dev --no-install-recommends && rm -r /var/lib/apt/lists/*

# Download And Install Last Phalcon
RUN git clone --depth=1 git://github.com/phalcon/cphalcon.git && cd cphalcon/build && sudo ./install && docker-php-ext-enable phalcon

# Remove Phalcon Git Directory
RUN cd ../../ && rm -rf ./cphalcon/
