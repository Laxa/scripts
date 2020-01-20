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
#https://github.com/michenriksen/aquatone/blob/854a5d56fbb7a00b2e5ec80d443026c7a4ced798/agents/url_screenshotter.go#L127
    timeout 3 google-chrome --headless --window-size=1920,1080 --ignore-certificate-errors --screenshot --incognito --disable-gpu --disable-crash-reporter --disable-notifications --no-first-run --disable-infobars --disable-sync --no-default-browser-check --proxy-server=http://127.0.0.1:8080 "${scheme}://${host}:${port}"
    mv "screenshot.png" out/"${host}_${port}.png"
    echo "${host}_${port}"
done < $FILE
