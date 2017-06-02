FROM bde2020/hadoop-base:1.1.0-hadoop2.7.1-java8
MAINTAINER Alexandre Abadie <alexandre.abadie@inria.fr>

RUN apt-get update -yqq  && apt-get install -yqq \
  wget \
  bzip2 \
  git \
  libglib2.0-0 \
  openssh-server \
  make build-essential \
  libssl-dev \
  zlib1g-dev \
  libbz2-dev \
  libreadline-dev \
  libsqlite3-dev \
  wget \
  curl \
  llvm \
  libncurses5-dev \
  libncursesw5-dev \
  xz-utils \
  tk-dev \
  && rm -rf /var/lib/apt/lists/*

# Configure environment
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /root

RUN git clone git://github.com/yyuu/pyenv.git .pyenv

ENV HOME  /root
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN pyenv install 2.7.8
RUN pyenv install 3.4.4
RUN pyenv install 3.5.3
RUN pyenv global 3.5.3
RUN pyenv rehash

RUN pip install tox
RUN pyenv local 2.7.8 3.4.4 3.5.3

ADD run.sh /run.sh
RUN chmod a+x /run.sh

CMD ["/run.sh"]