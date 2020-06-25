# Crawler an excercise

crawler finds all links on a site and based on rules explores and and interprets data

## Install

pip install .

## Use

crawler --help

## Test

pip install -r test_requirements.txt
pytest tests

## Issues / TODO

* Does not respect robots.txt expiration
* Does not respect robots.txt delay
* Missing input validation
* General cleanup an refactoring
