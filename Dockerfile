# WSGI service environment

FROM sourcepole/qwc-uwsgi-base:alpine-latest as base

# Required for pip with git repos
RUN apk add --no-cache --update git
# Required for psychopg, --> https://github.com/psycopg/psycopg2/issues/684
RUN apk add --no-cache --update postgresql-dev gcc python3-dev musl-dev

# maybe set locale here if needed

ADD . /srv/qwc_service
RUN pip3 install --no-cache-dir -r /srv/qwc_service/requirements.txt

ENV SERVICE_MOUNTPOINT=/api/v1/data


#When using debug target then install pydevd-pycharm.egg from pycharm
# asciidoc tag::debug[]
FROM base as debug
RUN pip install pydevd-pycharm~=203.7148.72
# asciidoc end::debug[]
