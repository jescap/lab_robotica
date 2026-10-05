
xhost +local:docker
docker run -it \
    --rm \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --env="ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --name lab_rob_container \
    --net=host \
    --privileged \
    --mount type=bind,source=/home/jescap/lab_rob_shared,target=/home/jescap/lab_rob_shared \
    lab_rob_image_ros2 \
    bash
