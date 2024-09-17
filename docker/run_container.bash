
xhost +local:docker
docker run -it \
    --env="DISPLAY=$DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --name lab_rob_container \
    --net=host \
    --privileged \
    --mount type=bind,source=/home/jescap/lab_robotica/exchange_dir,target=/home/lab_robotica/exchange_dir \
    lab_rob_image \
    bash
    
docker rm lab_rob_container
