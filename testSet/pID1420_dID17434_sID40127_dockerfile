FROM openjdk:8-jdk-alpine

RUN apk add --no-cache apache-ant
RUN mkdir -p /checker/tasks
ADD . /checker/tasks

USER nobody
WORKDIR /checker/tasks
ENTRYPOINT ["/usr/bin/ant"]
