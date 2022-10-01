#!/bin/bash
set -euxo pipefail

cd /opt/projects/star-burger/

git pull origin master

source .venv/bin/activate
pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate
deactivate

# You must add that commands to /etc/sudoers.d/ to escape avoid password asking
sudo systemctl restart starburger.service
sudo systemctl reload nginx.service

echo -e "\n\033[32m\033[1mSuccess build"
