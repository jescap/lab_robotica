FROM osrf/ros:noetic-desktop-full

SHELL ["/bin/bash", "-c"] 

# Required ROS packages  
RUN sudo apt update && apt install -y ros-noetic-joy ros-noetic-teleop-twist-joy \
    ros-noetic-teleop-twist-keyboard ros-noetic-laser-proc \
    ros-noetic-rgbd-launch ros-noetic-rosserial-arduino \
    ros-noetic-rosserial-python ros-noetic-rosserial-client \
    ros-noetic-rosserial-msgs ros-noetic-amcl ros-noetic-map-server \
    ros-noetic-move-base ros-noetic-urdf ros-noetic-xacro \
    ros-noetic-compressed-image-transport ros-noetic-rqt* ros-noetic-rviz \
    ros-noetic-gmapping ros-noetic-navigation ros-noetic-interactive-markers \
    ros-noetic-vision-msgs

# ROS packages for Turtlebot3 robot     
RUN sudo apt install -y ros-noetic-dynamixel-sdk \
    ros-noetic-turtlebot3-*

# We also install Git and file editors, just in case
RUN sudo apt install -y git vim nano iputils-ping net-tools

# MESA drivers for hardware acceleration graphics (Gazebo and RViz)
RUN sudo apt -y install libgl1-mesa-glx libgl1-mesa-dri && \
    rm -rf /var/lib/apt/lists/*

# Create a user provided as build argument
ARG USER_NAME=student
ARG USER_ID=1000
ARG GROUP_ID=${USER_ID}

RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash ${USER_NAME} && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Source the ROS installation
RUN echo "source /opt/ros/noetic/setup.bash" >> /home/${USER_NAME}/.bashrc && \
    echo "export TURTLEBOT3_MODEL=burger" >> /home/${USER_NAME}/.bashrc

# Working directory inside our container
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}/lab_rob_shared
