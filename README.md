# Remote End of DISORF
DISORF aims to train NeRF for 3d reconstruction in real-time. It uses distributed architecture so that the whole NeRF-SLAM system is divided into the SLAM part for collecting posed images and the NeRF training and visualization part. In this way, By designing specialized local-end for embedded devices like Jetson, we allow resource-constrained devices to leverage power of NeRF. This repository contains remote-end.

### Requirements
- A computer with Ubuntu 20.04
- ROS Noetic
- Nvidia GPU

### Installation  
We provide a script, setup_server_end.sh, to install and configure all dependencies. It will automatically create conda environment, install dependencies of Nerfstudio, and install ROS noetic. Use it with
```
source setup_server_end.sh
```

### Demo
Belwo is the demo for real-time reconstruction of replica dataset
[DISORF replica demo](https://www.youtube.com/watch?v=F54Ju3NsQ4g&ab_channel=Edward_Li)
Belwo is the demo for real-time reconstruction of real-world scenario
[DISORF real-world scenario demo](https://www.youtube.com/watch?v=34v2ecO8LjE&ab_channel=Edward_Li)))


### Acknowledgements:
We have utilized and modified portions of the code from [nerfbridge](https://github.com/javieryu/nerf_bridge) and [nerfstudio](https://github.com/nerfstudio-project/nerfstudio). We are deeply grateful to the developers and contributors of the two remarkable projects.
