FROM tkelman/julia64-part2:master
MAINTAINER Tony Kelman <tony@kelman.net>

RUN git clone https://github.com/JuliaLang/julia /home/julia-i686 && \
    cd /home/julia-i686 && \
    echo 'override ARCH = i686' >> Make.user && \
    echo 'override MARCH = pentium4' >> Make.user && \
    DEPS="openblas arpack suitesparse pcre gmp mpfr libgit2" && \
    INSTALL="" && DISTCLEAN="" && \
    for dep in $DEPS; do \
      INSTALL="$INSTALL install-$dep" && \
      DISTCLEAN="$DISTCLEAN distclean-$dep"; \
    done && \
    make -j2 -C deps $INSTALL && \
    make -C deps $DISTCLEAN
# distclean should leave in place the installed libraries and headers
WORKDIR /home/julia-i686
