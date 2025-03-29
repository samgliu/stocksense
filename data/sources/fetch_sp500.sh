#!/bin/bash
mkdir -p data/raw
curl -L -o data/raw/sp-500-stocks.zip \
  https://www.kaggle.com/api/v1/datasets/download/andrewmvd/sp-500-stocks
