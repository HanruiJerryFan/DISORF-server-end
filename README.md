# Remote End of DISORF
DISORF aims to train NeRF for 3d reconstruction in real-time. It uses distributed architecture so that the whole NeRF-SLAM system is divided into the SLAM part for collecting posed images and the NeRF training and visualization part. In this way, By designing specialized local-end for embedded devices like Jetson, we allow resource-constrained devices to leverage power of NeRF. This repository contains remote-end. It is developed upon nerfbridge (https://github.com/javieryu/nerf_bridge).

### Requirements
- A computer with Ubuntu 20.04
- ROS Noetic

### Installation  
We provide a script, setup_server_end.sh, to install and configure all dependencies. It will automatically create conda environment, install dependencies of Nerfstudio, and install ROS noetic. Use it with
```
source setup_server_end.sh
```

### Example Usage:


### Acknowledgements:
We have utilized and modified portions of the code from [nerfbridge](https://github.com/javieryu/nerf_bridge) and [nerfstudio](https://github.com/nerfstudio-project/nerfstudio). We are deeply grateful to the developers and contributors of the two remarkable projects.