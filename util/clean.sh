#!/bin/bash

BOLD=$(tput bold)
NORMAL=$(tput sgr0)

target[0]='*~'
target[1]='*.swp'
target[2]='.DS_Store'
# target[3]='*.log'
# target[4]='*.out'
# target[5]='*.aux'
# target[5]='*.synctex.gz'

limit=`expr ${#target[@]} - 1`

for i in $(seq 0 $limit);
do
  echo "${BOLD}Cleaning [${i}]: ${target[${i}]} ${NORMAL}"
  find . -name "${target[i]}" -exec rm -v {} \;
done
