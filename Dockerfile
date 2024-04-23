FROM python:3.11.7-slim-bookworm

#LABEL org.opencontainers.image.source=https://github.com/ethermeta-org/onesphere

COPY requirements.txt /tmp/requirements.txt

COPY . /workspace

COPY config.yaml /etc/anylinker/

COPY docker-entrypoint.sh /usr/local/bin/

RUN set -eux; \
	\
	apt-get update; \
	apt-get install -y --no-install-recommends curl; \
	pip install -r /tmp/requirements.txt

VOLUME ["/etc/anylinker"]

WORKDIR /workspace

ENTRYPOINT ["docker-entrypoint.sh.sh"]

CMD ["python3", "main.py", "--config", "/etc/anylinker/config.yaml"]