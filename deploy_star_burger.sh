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

LAST_COMMIT_HASH=$(git rev-parse --short HEAD)
ROLLBAR_ACCESS_TOKEN=<token>
ROLLBAR_ENVIRONMENT=production
USERNAME=$(whoami)
BUILD_STATUS=succeeded
curl --url https://api.rollbar.com/api/1/deploy \
  --request POST \
  --header "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
  --header "accept: application/json" \
  --header "content-type: application/json" \
  --data '{
    "environment":"'"$ROLLBAR_ENVIRONMENT"'",
    "revision":"'"$LAST_COMMIT_HASH"'",
    "rollbar_username":"'"$USERNAME"'",
    "local_username":"'"$USERNAME"'",
    "status":"'"$BUILD_STATUS"'"
  }'

echo -e "\n\033[32m\033[1mSuccess build"
