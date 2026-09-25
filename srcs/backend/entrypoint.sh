#This enterpoint is used to migrate the data (like admin user) to the db
#in Django everytime you want to modify the db you have to migrate

#!/bin/bash

# Stop the script if teher is an error
set -e

echo "Drawing the blueprints..."
python manage.py makemigrations test
python manage.py makemigrations

echo "Execution of the migration of the db..."
python manage.py migrate --fake-initial

echo "Automatic creation of the superuser (if he dosen't exixt)... "
python manage.py createsuperuser --noinput || true

echo "Starting the server..."
#The line down execute all the comand after the enterpoint
exec "$@"

