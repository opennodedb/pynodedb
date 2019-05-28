FROM lsiobase/alpine:3.9

LABEL maintainer 'Sam Burney <sam@burney.io>'

ENV PYNODEDB_LISTEN=0.0.0.0:5000 \
    PYNODEDB_SITENAME="pynodedb" \
    PYNODEDB_MAP_DEFAULT_CENTRE="Adelaide, South Australia, Australia" \
    PYNODEDB_GOOGLE_MAPS_API_KEY="api key" \
    PYNODEDB_DB_DRIVER="mysql" \
    PYNODEDB_DB_HOST="db" \
    PYNODEDB_DB_DATABASE="nodedb" \
    PYNODEDB_DB_USERNAME="nodedb" \
    PYNODEDB_DB_PASSWORD="password" \
    PYNODEDB_OAUTH_CLIENT_ID=0 \
    PYNODEDB_OAUTH_CLIENT_SECRET="secret key"

RUN apk add --update \
    git \
    python3 \
    gcc musl-dev python3-dev libffi-dev openssl-dev \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install cryptography \
    && apk del gcc musl-dev python3-dev libffi-dev openssl-dev \
    && rm -rf /tmp/* /var/tmp/* /var/cache/apk/* /var/cache/distfiles/* /root/.cache/pip

RUN git clone https://git.sifnt.net.au/sam/pynodedb.git /usr/local/share/pynodedb \
    && cd /usr/local/share/pynodedb \
    && git submodule init \
    && git submodule update --recursive \
    && python3 -m pip install -e /usr/local/share/pynodedb

ADD ./docker/root/ /

EXPOSE 5000/tcp

ENTRYPOINT [ "/init" ]
