#!/bin/bash

# Clean up Docker containers created by act (GitHub Actions local runner)

# Remove all stopped containers created by act
docker ps -a --filter "label=act" --format "{{.ID}}" | xargs -r docker rm

# Remove all act containers (both running and stopped)
# Uncomment the following line if you want to force remove running containers too
# docker ps -a --filter "label=act" --format "{{.ID}}" | xargs -r docker rm -f

# Clean up dangling images created by act
docker image prune -f --filter "label=act"

# Optional: Remove all act-related volumes
# docker volume ls --filter "label=act" --format "{{.Name}}" | xargs -r docker volume rm

echo "Act containers cleaned up successfully"