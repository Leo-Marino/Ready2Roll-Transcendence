#This enterpoint is used to migrate the data (like admin user) to the db
#in Django everytime you want to modify the db you have to migrate

#!/bin/bash

# Stop the script if there is an error
set -e

# 1.  Waits (max 90s) for Vault Agent to render the file, then loads it into
# the process environment only.
i=0
until [ -s /vault/secrets/django.env ]; do
  i=$((i+1))
  if [ "$i" -gt 90 ]; then
    echo "FATAL: vault agent did not render django.env (is Vault sealed?)"
    exit 1
  fi
  echo "waiting for vault agent... ($i/90)"
  sleep 1
done
set -a; . /vault/secrets/django.env; set +a

# 2. Database
echo "Creating migrations..."
python manage.py makemigrations --noinput users events social notifications

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Automatic creation of the superuser (if he dosen't exist)... "
python manage.py createsuperuser --noinput || true

echo "Starting the server..."
#The line down execute all the comand after the entrypoint
exec "$@"

