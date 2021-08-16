FROM centos:latest
MAINTAINER Vaclav Sykora <vaclav.sykora@gmail.com>

# Make systemd aware about the fact that it runs inside a container.
# Systemd is now included in both the centos:7 and centos:latest base containers, but it is not active by default.
# See here for more info: https://hub.docker.com/_/centos/
ENV container docker

# update all repos
RUN set -x \
        && yum -y update centos-release \
        && yum -y update

# remove unneeded dependencies
RUN sed -ir -e '$a clean_requirements_on_remove=1' /etc/yum.conf

# helpful tools
RUN set -x \
        && yum -y install sudo nano vim wget telnet man yum-utils net-tools bind-utils psmisc tar curl lsof \
        && yum clean all

# prompt
ENV PS1 "\[\e[1;33m\][centos] [\u@\h \w]$ \[\e[0m\]"
# set correct time zone
RUN ln -fs /usr/share/zoneinfo/Europe/Prague /etc/localtime

# cleanup
RUN rm -fr /tmp/* \
        && yum clean -y all
