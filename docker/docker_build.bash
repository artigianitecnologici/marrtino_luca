#!/bin/bash

MACHTYPE=`uname -m`

UPAR="--build-arg UID=`id -u` --build-arg GID=`id -g`"

if [ "$MACHTYPE" = "x86_64" ]; then
  docker pull iocchi/orazio
  #docker build -t orazio -f Dockerfile.orazio . && \
  #docker tag orazio iocchi/orazio && \
  #docker build -t iocchi/orazio:2018 -f Dockerfile.orazio2018 .
else
  docker pull iocchi/orazio:arm64
  #docker build -t orazio -f Dockerfile.orazio . && \
  #docker tag orazio iocchi/orazio:arm64 && \
  #docker build -t iocchi/orazio:2018-arm64 -f Dockerfile.orazio2018 .
fi && \
docker build $UPAR -t marrtino:system -f Dockerfile.system . && \
docker build -t marrtino:base -f Dockerfile.base . && \
docker build -t marrtino:teleop -f Dockerfile.teleop . && \
docker build -t marrtino:navigation -f Dockerfile.navigation . && \
docker build -t marrtino:vision -f Dockerfile.vision . && \
docker build -t marrtino:speech -f Dockerfile.speech . && \
docker build -t marrtino:mapping -f Dockerfile.mapping . && \
docker build -t marrtino:pantilt -f Dockerfile.pantilt .

#docker build $UPAR -t marrtino:objrec -f Dockerfile.objrec .

