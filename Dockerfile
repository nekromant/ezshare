FROM debian:bullseye-slim

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y davfs2 ca-certificates python3-pip
COPY . /app/
RUN cd /app && pip3 install .

ENTRYPOINT /app/docker/start.sh

