#!/usr/bin/env bash


BASEDIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )
FILENAME_BASE=${BASEDIR##*/}

echo $(pip install --prefix=${BASEDIR}/bin  splunk-sdk )
echo $(pip install --prefix=${BASEDIR}/bin  requests )
echo $(mv "${BASEDIR}/bin/lib/python2.7/site-packages/splunklib" "${BASEDIR}/bin")
echo $(mv "${BASEDIR}/bin/lib/python2.7/site-packages/requests" "${BASEDIR}/bin")
echo $(rm -rf "${BASEDIR}/bin/lib")


