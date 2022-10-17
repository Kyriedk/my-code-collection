FROM python:3.10.8

WORKDIR /usr/src/app

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

RUN install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
    vim \
    curl \
    procps \
    findutils\
    jq

CMD ["python"]
