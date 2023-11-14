# Copyright 2022 the Regents of the University of California, Nerfstudio Team and contributors. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Abstracts for the Pipeline class.
"""
from __future__ import annotations
import os
from abc import abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from time import time
from typing import Optional, Type

import numpy as np
import torch
from PIL import Image
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from nsros.ros_datamanager import ROSDataManager
from nerfstudio.utils import profiler
from nerfstudio.pipelines.base_pipeline import VanillaPipeline, VanillaPipelineConfig
from nerfstudio.pipelines.dynamic_batch import DynamicBatchPipeline, DynamicBatchPipelineConfig

@dataclass
class ROSPipelineConfig(VanillaPipelineConfig):
    """ROS Pipeline Config."""
    _target: Type = field(default_factory=lambda: ROSPipeline)
    save_eval_images: bool = True
    """Whether to save eval rendered images to disk."""
    output_dir: Optional[Path] = None
    """Path to save eval rendered images to."""
    get_std: bool = True
    """Whether to return std with the mean metric in eval output."""
    eval_idx_list: str = ""

class ROSPipeline(VanillaPipeline):
    """Pipeline class for ROS."""
    config: ROSPipelineConfig
    datamanager: ROSDataManager

    @profiler.time_function
    def get_average_eval_image_metrics(self, step: Optional[int] = None):
        """Iterate over all the images in the eval dataset and get the average.

        Args:
            step: current training step
            output_path: optional path to save rendered images to
            get_std: Set True if you want to return std with the mean metric.

        Returns:
            metrics_dict: dictionary of metrics
        """
        self.eval()
        metrics_dict_list = []
        assert isinstance(self.datamanager, ROSDataManager)
        
        if self.datamanager.config.eval_with_training_set and \
          hasattr(self.model.field, "use_training_cameras"):
            self.model.field.use_training_cameras = True

        num_images = len(self.datamanager.fixed_indices_eval_dataloader)

        eval_idx_list = None
        if self.config.eval_idx_list != "":
            eval_idx_list = np.loadtxt(self.config.eval_idx_list, dtype=int)
            num_images = len(eval_idx_list)

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            MofNCompleteColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[green]Evaluating all eval images...", total=num_images)
            for i, (camera_ray_bundle, batch) in enumerate(self.datamanager.fixed_indices_eval_dataloader):
                if eval_idx_list is not None and i not in eval_idx_list:
                    continue
                # time this the following line
                inner_start = time()
                height, width = camera_ray_bundle.shape
                num_rays = height * width
                outputs = self.model.get_outputs_for_camera_ray_bundle(camera_ray_bundle)
                metrics_dict, images_dict = self.model.get_image_metrics_and_images(outputs, batch)

                if self.config.save_eval_images:
                    camera_indices = camera_ray_bundle.camera_indices
                    output_path = self.config.output_dir / f"{step:06d}" if step is not None else ""
                    os.makedirs(output_path, exist_ok=True)
                    assert camera_indices is not None
                    for key, val in images_dict.items():
                        if key == 'img':
                            Image.fromarray((val * 255).byte().cpu().numpy()).save(
                                output_path / "{0:06d}-{1}.jpg".format(int(camera_indices[0, 0, 0]), key)
                            )
                assert "num_rays_per_sec" not in metrics_dict
                metrics_dict["num_rays_per_sec"] = num_rays / (time() - inner_start)
                fps_str = "fps"
                assert fps_str not in metrics_dict
                metrics_dict[fps_str] = metrics_dict["num_rays_per_sec"] / (height * width)
                metrics_dict_list.append(metrics_dict)
                progress.advance(task)
        # average the metrics list
        metrics_dict = {}
        for key in metrics_dict_list[0].keys():
            if self.config.get_std:
                key_std, key_mean = torch.std_mean(
                    torch.tensor([metrics_dict[key] for metrics_dict in metrics_dict_list])
                )
                metrics_dict[key] = float(key_mean)
                metrics_dict[f"{key}_std"] = float(key_std)
            else:
                metrics_dict[key] = float(
                    torch.mean(torch.tensor([metrics_dict[key] for metrics_dict in metrics_dict_list]))
                )
        # metrics_dict["All PSNR"] = [{"psnr": metrics_dict["psnr"]} for metrics_dict in metrics_dict_list]
        self.train()
        return metrics_dict
    

@dataclass
class ROSDynamicBatchPipelineConfig(DynamicBatchPipelineConfig):
    """ROS Dynamic Batch Pipeline Config."""
    _target: Type = field(default_factory=lambda: ROSDynamicBatchPipeline)
    save_eval_images: bool = True
    """Whether to save eval rendered images to disk."""
    output_dir: Optional[Path] = None
    """Path to save eval rendered images to."""
    get_std: bool = True
    """Whether to return std with the mean metric in eval output."""
    eval_idx_list: str = ""

class ROSDynamicBatchPipeline(DynamicBatchPipeline):

    @profiler.time_function
    def get_average_eval_image_metrics(self, step: Optional[int] = None):
        """Iterate over all the images in the eval dataset and get the average.

        Args:
            step: current training step
            output_path: optional path to save rendered images to
            get_std: Set True if you want to return std with the mean metric.

        Returns:
            metrics_dict: dictionary of metrics
        """
        self.eval()
        metrics_dict_list = []
        assert isinstance(self.datamanager, ROSDataManager)

        if self.datamanager.config.eval_with_training_set and \
          hasattr(self.model.field, "use_training_cameras"):
            self.model.field.use_training_cameras = True
        
        num_images = len(self.datamanager.fixed_indices_eval_dataloader)

        eval_idx_list = None
        if self.config.eval_idx_list != "":
            eval_idx_list = np.loadtxt(self.config.eval_idx_list, dtype=int)
            num_images = len(eval_idx_list)

        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            MofNCompleteColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[green]Evaluating all eval images...", total=num_images)
            for i, (camera_ray_bundle, batch) in enumerate(self.datamanager.fixed_indices_eval_dataloader):
                if eval_idx_list is not None and i not in eval_idx_list:
                    continue
                # time this the following line
                inner_start = time()
                height, width = camera_ray_bundle.shape
                num_rays = height * width
                outputs = self.model.get_outputs_for_camera_ray_bundle(camera_ray_bundle)
                metrics_dict, images_dict = self.model.get_image_metrics_and_images(outputs, batch)

                if self.config.save_eval_images:
                    camera_indices = camera_ray_bundle.camera_indices
                    output_path = self.config.output_dir / f"{step:06d}" if step is not None else ""
                    os.makedirs(output_path, exist_ok=True)
                    assert camera_indices is not None
                    for key, val in images_dict.items():
                        if key == 'img':
                            Image.fromarray((val * 255).byte().cpu().numpy()).save(
                                output_path / "{0:06d}-{1}.jpg".format(int(camera_indices[0, 0, 0]), key)
                            )
                assert "num_rays_per_sec" not in metrics_dict
                metrics_dict["num_rays_per_sec"] = num_rays / (time() - inner_start)
                fps_str = "fps"
                assert fps_str not in metrics_dict
                metrics_dict[fps_str] = metrics_dict["num_rays_per_sec"] / (height * width)
                metrics_dict_list.append(metrics_dict)
                progress.advance(task)
        # average the metrics list
        metrics_dict = {}
        for key in metrics_dict_list[0].keys():
            if self.config.get_std:
                key_std, key_mean = torch.std_mean(
                    torch.tensor([metrics_dict[key] for metrics_dict in metrics_dict_list])
                )
                metrics_dict[key] = float(key_mean)
                metrics_dict[f"{key}_std"] = float(key_std)
            else:
                metrics_dict[key] = float(
                    torch.mean(torch.tensor([metrics_dict[key] for metrics_dict in metrics_dict_list]))
                )
        # metrics_dict["All PSNR"] = [{"psnr": metrics_dict["psnr"]} for metrics_dict in metrics_dict_list]
        self.train()
        return metrics_dict
    