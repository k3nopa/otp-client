#!/bin/bash

docker run --rm -d --name emqx -p 127.0.0.1:1883:1883 -p 8081:8081 -p 8083:8083 -p 8883:8883 -p 8084:8084 -p 18083:18083 emqx/emqx
