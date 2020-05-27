#!/bin/bash

sudo -u postgres psql -c "DROP DATABASE trivia_test;" &&
sudo -u postgres psql -c "CREATE DATABASE trivia_test;"  &&
psql trivia_test < trivia.psql  &&
python test_flaskr.py