#!/bin/bash

set -e

# cd lambda/scraper

rm -f dist/index.zip
npm run build
zip -j dist/index.zip dist/index.js
rm dist/index.js