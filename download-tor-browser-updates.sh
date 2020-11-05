#!/bin/bash -ex

download_and_verify() {
    set -e
    version=$1
    apk=$2
    cd $(mktemp -d)
    if ! wget --quiet --continue https://dist.torproject.org/torbrowser/${version}/${apk}.asc; then
	printf "\nERROR $apk\n\n"
	return
    fi

    wget --quiet --continue https://dist.torproject.org/torbrowser/${version}/${apk}
    if gpg --verify ${apk}.asc; then
	rsync -axv \
	      ${apk} \
	      ${apk}.asc \
              $basedir/repo/
    fi
    rm ${apk} \
       ${apk}.asc
}


basedir=`cd $(dirname $0); pwd`
http_proxy=http://localhost:54321
https_proxy=http://localhost:8081
SOCKS_SERVER=locahost:9050

if [ "`curl --silent https://check.torproject.org/api/ip | jq .IsTor`" != "true" ]; then
    echo ERROR not running over tor!
    exit 1
fi

urls=""
for version in `curl --silent https://dist.torproject.org/torbrowser/ | sed -En 's,.*>([0-9]+\.[0-9.a]+)/?<.*,\1,p'`
do
    for arch in aarch64 armv7 x86_64 x86; do
	apk=tor-browser-${version}-android-${arch}-multi.apk
	if [ -e $basedir/archive/$apk ]; then
	    echo Skipping archived $apk
	elif [ -e $basedir/repo/$apk ]; then
	    echo Skipping existing repo $apk
	else
	    download_and_verify $version $apk &
	fi
    done
    wait
done
