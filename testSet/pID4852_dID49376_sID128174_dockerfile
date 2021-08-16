# shout
# Run shout (https://github.com/erming/shout)
#
# VERSION               0.0.2

FROM            debian:jessie
MAINTAINER      Vishal Doshi (vishal.doshi@gmail.com)

# Don't want to pollute the env with DEBIAN_FRONTEND
RUN apt-get update && apt-get install -y nodejs npm git
RUN ln -sf /usr/bin/nodejs /usr/bin/node
RUN git clone https://github.com/erming/shout /root/app
WORKDIR /root/app
RUN npm install 
RUN /usr/bin/node index.js add demo demo
ENTRYPOINT ["/usr/bin/node", "index.js"]
EXPOSE 9000
