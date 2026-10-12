xhost +localhost
docker run -it \
    --rm \
    --env="DISPLAY=host.docker.internal:0" \
    --env="ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST" \
    --name lab_rob_container \
    --net=host \
    --privileged \
    --mount type=bind,source=/home/[USER]/lab_rob_shared,target=/home/[USER]/lab_rob_shared \
    lab_rob_image \
    bash
