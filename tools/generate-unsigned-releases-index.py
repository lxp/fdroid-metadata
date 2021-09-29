#!/home/members/nfreitas/sites/guardianproject.info/users/gpbuilds/pyvenv/bin/python
#
# This is a quick hack to make it easy to download APKs from
# https://guardianproject.info/releases/?C=M;O=D
#
# To deploy, build a venv locally and then set it up on gpbuilds:
#
#  sudo mkdir -p /home/members/nfreitas/sites/guardianproject.info/users/gpbuilds
#  sudo chown $USER /home/members/nfreitas/sites/guardianproject.info/users/gpbuilds
#  cd /home/members/nfreitas/sites/guardianproject.info/users/gpbuilds
#  python3 -m venv --copies --clear pyvenv
#  . pyvenv/bin/activate
#  pip install --upgrade pip
#  rsync -axvz pyvenv gpbuilds:/home/members/nfreitas/sites/guardianproject.info/users/gpbuilds/
#  ssh gpbuilds
#  . ~/pyvenv/bin/activate
#  pip install fdroidserver

import androguard.core.bytecodes.apk
import collections
import glob
import logging
import os
import sys
from fdroidserver import common, index, metadata, update
from urllib.parse import urlsplit, urlunsplit


class Options:
    allow_disabled_algorithms = True
    clean = False
    delete_unknown = False
    nosign = True
    pretty = True
    rename_apks = False
    verbose = True


def main():
    repodir = os.getcwd()
    index_file = 'index-v1.json'
    newest = 0.0
    for f in glob.glob('*.apk') + glob.glob('*.apk.sig') + glob.glob('*.apk.asc'):
        mtime = os.path.getmtime(f)
        if mtime > newest:
            newest = mtime
            print(mtime, f, sep='\t')
    if os.path.exists(index_file) and os.path.getmtime(index_file) > newest:
        print(index_file, 'is current.')
        exit(0)

    logging.getLogger().setLevel(logging.DEBUG)

    update.config = common.read_config(Options)
    update.options = Options
    update.config['apksigner'] = '/bin/true'  # gpbuilds server has no Java :'-(
    update.config['repo_pubkey'] = 'dead'

    apps = {}
    for f in glob.glob('*.apk'):
        appid, versionCode, _ = androguard.core.bytecodes.apk.get_apkid(f)
        if appid in apps:
            app = apps[appid]
            if int(versionCode) > int(app['CurrentVersionCode']):
                app['CurrentVersionCode'] = versionCode
            continue
        app = metadata.App()
        app['id'] = appid
        app['icon'] = 'fake.png'
        app['CurrentVersionCode'] = versionCode
        app['License'] = 'placeholder'
        app['WebSite'] = 'placeholder'
        apps[appid] = app
        print(appid)

    knownapks = common.KnownApks()
    apkcache = update.get_cache()
    apks, cache_changed = update.process_apks(apkcache, repodir, knownapks)
    files, file_cache_changed = update.scan_repo_files(apkcache, repodir, knownapks)
    if cache_changed or file_cache_changed:
        update.write_cache(apkcache)

    allrepofiles = apks + files
    update.read_added_date_from_all_apks(apps, allrepofiles)
    sortedapps = collections.OrderedDict()
    for appid in sorted(apps.keys()):
        sortedapps[appid] = apps[appid]
    index.make_v1(sortedapps, apks, repodir, {}, {}, {})
    knownapks.writeifchanged()

    # clean up icon cruft that's not used at all
    for appid in sortedapps:
        for f in sorted(glob.glob('icons*/' + appid + '*.[0-9]*.png')):
            os.remove(f)
    for d in glob.glob('icons*'):
        if os.path.isdir(d):
            print(d)
            try:
                os.rmdir(d)
            except OSError as e:
                print(e)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])
    main()
