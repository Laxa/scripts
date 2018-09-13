#!/bin/sh

#set -x

while read IP; do
    if [ ! -f "nmap_${IP}-all-ports.gnmap" ]
    then
        echo "${IP} not found"
        continue
    fi
    PORTS=$(egrep -o '[0-9]{1,5}/open' "nmap_${IP}-all-ports.gnmap" | cut -d '/' -f 1 | tr '\n' ',' | rev | cut -c 2- | rev)
    echo "${IP} found: ${PORTS}"
    if [ -z "$PORTS" ]
    then
        continue
    fi
    nmap -vvv -T2 "-p${PORTS}" -sC -sV -oA "nmap_${IP}-services" "$IP" &
done<hosts.txt
