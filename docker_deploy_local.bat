docker stop sprites
docker rm sprites
docker build --no-cache -t sprites .
docker run --restart=unless-stopped --name=sprites -d -it -p 9000:9000 sprites
docker system prune -f
