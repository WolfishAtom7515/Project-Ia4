#!/bin/bash

IMAGE_NAME="myapp"
HOST_PORT="5000"
CONTAINER_PORT="5000"
INSTANCE_VOLUME="e:/Develop/Ia1/Lab2/instance:/usr/src/app/instance"
UPLOADS_VOLUME="e:/Develop/Ia1/Lab2/Website/static/uploads:/usr/src/app/Website/static/uploads"

echo "Building Docker in process.."
docker build -t "$IMAGE_NAME" .
if [ $? -ne 0 ]; then
	echo "Failed to build Docker!"
	exit 1
fi
echo "Built succesfully!"

echo "Running the docker file.."
docker run --privileged -p "$HOST_PORT:$CONTAINER_PORT" \
  -v "$INSTANCE_VOLUME" \
  -v "$UPLOADS_VOLUME" \
  "$IMAGE_NAME"
if [ $? -ne 0 ]; then
	echo "Failed to run!"
	exit 1
fi
echo "Run succesfully!"
