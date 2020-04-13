echo "Enabling Virtualenv..."
source /home/sprites/sprites/bin/activate

echo "Downloading updates from Git..."
sudo git checkout .
sudo git pull

echo "Installing Python dependencies..."
sudo pip install -r requirements.txt --quiet

echo "Gathering static files..."
sudo ./manage.py collectstatic --noinput

echo "Restarting Gunicorn..."
sudo systemctl restart gunicorn

echo "Restarting nginx..."
sudo nginx -t && sudo systemctl restart nginx

echo "Done!"
