#!/bin/bash

docker system prune -a --volumes
docker image prune 
docker volume prune 
docker network prune 

exit 0
