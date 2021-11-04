#!/bin/sh

cd ../../../

python ./setup.py sdist --formats=gztar

gsutil cp dist/waveform_fun-0.0.tar.gz gs://physionet_2009/model_pkgs/
