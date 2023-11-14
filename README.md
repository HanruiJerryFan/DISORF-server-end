# Remote End of DISORF
DISORF aims for training NeRF for 3d reconstruction in real-time. It uses distributed archeture so that the whole NeRF-SLAM system is divided into the SLAM part for collecting posed images and the NeRF training and visualization part. In this way, By designing specialized local-end for embedded devices like Jetson, we allow resource-constrained devices to leverage power of NeRF. This repository contains remote-end. It is developed upon nerfbridge (https://github.com/javieryu/nerf_bridge).

### Requirements
- A computer with Ubuntu 20.04
- ROS Noetic

### Installation  
We provide a script, setup_server_end.sh, to install and configure all dependencies. It will automatically create conda environment, install dependencies of Nerfstudio, and install ROS noetic. Use it with
```
source setup_server_end.sh
```

### Example Usage:
```
python3 ros_train.py --experiment-name test --method-name ros_nerfacto --data data/ros/test --pipeline.datamanager.dataparser.ros-data TUM_config_office.json --draw-training-images True --pipeline.datamanager.data_update_freq 60 --pipeline.datamanager.camera_optimizer.mode off --vis viewer+tensorboard --steps_per_eval_all_images 7999
```
To train a NeRF via server_end:
```
python3 ros_train.py --method-name ros_nerfacto --data path/to/save --pipeline.datamanager.dataparser.ros-data TUM_config_office.json --draw-training-images True
```
To use nerfstudio viewer:
```
ns-viewer --load-config outputs/path/to/config.yml
```
To create nsros ``whl`` file use code below, find ``whl`` file in ``dist`` and then use ``pip install *.whl``
```
python3 setup.py bdist_wheel
```
Convert SLAM transform matrix, output is ``matrix_converted.json``:
```
python3 converter.py matrix.json
```
Use ``frame_sampler.py`` to generate evaluation dataset and ``camera_path.json``, below is an example usage:
```
python3 frame_sampler.py 30 uniform path/to/data path/to/output
```
To render evaluation image:
```
ns-render camera-path --load-config outputs/path/to/config.yml --camera-path-filename data/path/to/camera_paths/*.json --output-path renders/* --output-format images
```
