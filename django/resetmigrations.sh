#!/bin/bash

# Remove all migrations and load database with csv datafile

rm -f db.sqlite3 recommender/migrations/0*.py recommender/migrations/__pycache__/0*.pyc
python manage.py makemigrations && python manage.py migrate
python manage.py makemigrations recommender && python manage.py migrate recommender
# python manage.py migrate recommender zero && python manage.py makemigrations && python manage.py migrate


# Now load data from csv file
./sqlite3 db.sqlite3 -cmd ".mode csv" ".import data.csv recommender_musicdata"

echo "*********************************************"
echo "If needed, now create super user and insert data into database"

$SHELL
