#!/bin/sh -e

basedir=$(cd $(dirname $0)/..; pwd)
cd $basedir
tmpdir=`mktemp --directory /tmp/.$(basename $0 | sed s,/,_,g).XXXXXXXXXX`

for f in `grep -Eo 'https?://[^"]+/fdroid/repo' index.html |sort -u`;  do
    dir=$tmpdir/`echo $f | sed -e 's,https?://,,' -e 's,/,_,g'`
    echo $dir
    mkdir $dir
    curl $f/index-v1.jar > $dir/index-v1.jar
    cd $dir
    unzip index-v1.jar index-v1.json || true
done

cd $tmpdir
echo '--------------------------------------------'
ls -l */index-v1.jar
echo '--------------------------------------------'
ls -l */index-v1.json
echo '--------------------------------------------'
ls -1 */index-v1.jar  | sed 's,jar$,,'  | sort > jar
ls -1 */index-v1.json | sed 's,json$,,' | sort > json
diff -uw jar json
