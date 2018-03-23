#!/bin/bash
docker build . -t ckevi/binverter:latest
docker tag ckevi/binverter:latest ckevi/binverter:1.2
docker push ckevi/binverter:latest
docker push ckevi/binverter:1.2
