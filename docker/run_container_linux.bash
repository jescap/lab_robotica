
xhost +local:docker
docker run -it \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --name lab_rob_container \
    --net=host \
    --privileged \
    --mount type=bind,source=/home/[USER]/lab_rob_shared,target=/home/[USER]/lab_rob_shared \
    lab_rob_image \
    bash
    
docker rm lab_rob_container
