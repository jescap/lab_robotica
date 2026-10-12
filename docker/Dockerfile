FROM osrf/ros:jazzy-desktop-full

SHELL ["/bin/bash", "-c"]

# Required ROS 2 packages. Gazebo (now called "Gazebo Harmonic", integrated through
# the ros_gz bridge) is already included in the jazzy-desktop-full image as part of
# its "simulation" meta-package, so there is no separate Gazebo install step here.
RUN sudo apt update && sudo apt install -y ros-jazzy-joy ros-jazzy-teleop-twist-joy \
    ros-jazzy-teleop-twist-keyboard \
    ros-jazzy-compressed-image-transport ros-jazzy-rqt* ros-jazzy-rviz2 \
    ros-jazzy-cartographer ros-jazzy-cartographer-ros \
    ros-jazzy-navigation2 ros-jazzy-nav2-bringup \
    ros-jazzy-interactive-markers ros-jazzy-vision-msgs ros-jazzy-xacro

# We also install Git, file editors, and the colcon/rosdep build tools, just in case
RUN sudo apt install -y git vim nano iputils-ping net-tools \
    python3-colcon-common-extensions python3-rosdep

# MESA drivers for hardware acceleration graphics (Gazebo and RViz2). Package names
# changed with respect to the ROS 1 image (Ubuntu 20.04): there is no more
# libgl1-mesa-glx in Ubuntu 24.04, its functionality now lives in libglx-mesa0.
RUN sudo apt -y install libgl1-mesa-dri libglx-mesa0 && \
    rm -rf /var/lib/apt/lists/*

# Create a user provided as build argument
ARG USER_NAME=student
ARG USER_ID=1000
ARG GROUP_ID=${USER_ID}

# The Ubuntu 24.04 base image already ships a default "ubuntu" user/group at
# UID/GID 1000, which collides with the host's typical first-user UID/GID
# (also 1000) passed in here. Remove that pre-existing user/group first if it
# occupies the UID/GID we were asked to use, then create ours normally.
RUN if getent passwd ${USER_ID} > /dev/null; then \
        userdel -r $(getent passwd ${USER_ID} | cut -d: -f1); \
    fi && \
    if getent group ${GROUP_ID} > /dev/null; then \
        groupdel $(getent group ${GROUP_ID} | cut -d: -f1); \
    fi && \
    groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash ${USER_NAME} && \
    echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ROS packages for the Turtlebot3 robot. Unlike ROS 1 (ros-noetic-turtlebot3-*),
# there is still no ready-made apt meta-package for this distro, so we build the
# official packages from source into a system-wide workspace, following ROBOTIS'
# own instructions.
RUN source /opt/ros/jazzy/setup.bash && \
    mkdir -p /home/${USER_NAME}/turtlebot3_ws/src && cd /home/${USER_NAME}/turtlebot3_ws/src && \
    git clone -b jazzy https://github.com/ROBOTIS-GIT/DynamixelSDK.git && \
    git clone -b jazzy https://github.com/ROBOTIS-GIT/turtlebot3_msgs.git && \
    git clone -b jazzy https://github.com/ROBOTIS-GIT/turtlebot3.git && \
    git clone -b jazzy https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git && \
    cd /home/${USER_NAME}/turtlebot3_ws && \
    colcon build --symlink-install && \
    chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/turtlebot3_ws

# Source the ROS installation and our Turtlebot3 workspace.
RUN echo "source /opt/ros/jazzy/setup.bash" >> /home/${USER_NAME}/.bashrc && \
    echo "source /home/${USER_NAME}/turtlebot3_ws/install/setup.bash" >> /home/${USER_NAME}/.bashrc && \
    echo "export TURTLEBOT3_MODEL=burger" >> /home/${USER_NAME}/.bashrc

# Working directory inside our container
USER ${USER_NAME}
WORKDIR /home/${USER_NAME}/lab_rob_shared
