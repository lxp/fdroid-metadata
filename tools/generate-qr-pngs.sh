#!/bin/sh -e

basedir=$(cd $(dirname $0)/..; pwd)
cd $basedir

for url in `grep -Eo 'https?://[^"]+/fdroid/repo\?fingerprint=[A-Z0-9]+' index.html |sort -u`;  do
    filename=`echo $url | sed -E -e 's,https?://,,' -e 's,/,_,g' -e 's,\?fingerprint=[A-Z0-9]+$,,'`-QR.png
    qr $url > $filename
    if ! grep -F $filename index.html; then
	echo "$filename missing in index.html"
	exit 1
    fi
done
