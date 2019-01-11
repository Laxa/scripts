#!/bin/bash

#set -x

FILE=FILE.CSV

while read p; do
    host=$(echo "$p" | cut -d ',' -f1 | tr -d '"')
    port=$(echo "$p" | cut -d ',' -f3 | tr -d '"')
    scheme='https'
    if [ $port -eq 80 ]; then
        scheme='http'
    fi
    timeout 3 google-chrome --headless --window-size=1920,1080 --ignore-certificate-errors --screenshot --proxy-server=http://127.0.0.1:8080 "${scheme}://${host}:${port}"
    mv "screenshot.png" out/"${host}_${port}.png"
    echo "${host}_${port}"
done < $FILE
