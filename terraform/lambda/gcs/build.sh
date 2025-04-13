#!/bin/bash
set -e

rm -rf dist
mkdir -p dist

pip install -r requirements.txt -t dist/
cp main.py dist/

rm -f dist/index.zip

cd dist
zip -r index.zip ./*
cd -