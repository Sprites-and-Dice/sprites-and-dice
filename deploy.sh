echo "Enabling Virtualenv..."
source /home/sprites/sprites/bin/activate

echo "Downloading updates from Git..."
git reset --hard
git clean -df
git checkout .
git pull

echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo "Gathering static files..."
./manage.py collectstatic --noinput

echo "Fixing file permissions..."
sudo chown -R sprites:sprites .

echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "Restarting nginx..."
sudo nginx -t && sudo systemctl restart nginx

echo "Done!"
