#!/bin/bash

# Change directory and check if successful
cd ~/checks-be/workswave-backend || exit 1

# Git commands - each one checks for success
git fetch origin || exit 1
git checkout develop || exit 1
git reset --hard origin/develop || exit 1

# Docker cleanup commands
# Using set -e to ensure script exits on any error
set -e

# Stop all containers (ignore error if no containers exist)
docker stop $(docker ps -aq) || true

# Remove all containers
docker rm $(docker ps -aq) || true

# Remove all images (trying both ways)
docker rmi $(docker images -q) || true
docker rmi -f $(docker images -q) || true

# Prune various docker resources with automatic yes
yes | docker system prune -a || true
yes | docker volume prune || true
yes | docker builder prune || true

# Remove all volumes
docker volume rm $(docker volume ls -q) || true

# Finally, build and start containers
docker-compose -f docker-compose.yml up --build -d

# health check
echo "Waiting for application to start..."
max_attempts=4  # 최대 20초 대기 (5초 x 4번)
attempt=1
while [ $attempt -le $max_attempts ]; do
   status_code=$(curl -s -o /dev/null -w "%{http_code}" localhost:80/docs)
   if [ "$status_code" = "200" ]; then
       echo "Health check passed: /docs endpoint returned 200"
       exit 0
   fi
   echo "Attempt $attempt of $max_attempts: Waiting for service to be ready... (Status code: $status_code)"
   sleep 5
   attempt=$((attempt + 1))
done

echo "Health check failed: /docs endpoint did not return 200 after $max_attempts attempts"
echo "Last status code: $status_code"
exit 1

# Reset error handling
set +e
