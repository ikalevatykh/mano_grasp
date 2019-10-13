# Learning Joint Reconstruction of Hands and Manipulated Objects - ManoGrasp

Porting the [MANO](http://mano.is.tue.mpg.de/) hand model to [GraspIt!](http://graspit-simulator.github.io/) simulator

Yana Hasson, Gül Varol, Dimitris Tzionas, Igor Kalevatykh, Michael J. Black,  Ivan Laptev, Cordelia Schmid, CVPR 2019

- [Project page](https://hassony2.github.io/obman)

## Install

### Setup ROS interface

This package uses a ROS [interface](https://github.com/graspit-simulator/graspit_commander) for the GraspIt! simulator.

To install and setup this interface follow the instructions at https://github.com/graspit-simulator/graspit_interface.

### Install package

```
git clone https://github.com/ikalevatykh/mano_grasp.git
cd mano_grasp
python setup.py install --user --graspit_dir=$GRASPIT
```

## Model

Model ManoHand will be automatically copied to $GRASPIT directory during the installation.

To copy a model without the code installation use the command:

    python setup.py --copy_model_only --graspit_dir=$GRASPIT


## Generate grasps

Start [ROS master](http://wiki.ros.org/roscore) in one terminal:

    roscore

Then in a second terminal start generator:

    python -m mano_grasp.generate_grasps --models phone glass --path_out PATH_TO_DATASET

Use 

    python -m mano_grasp.generate_grasps --help

to see all available options.

# Citations

If you find this code useful for your research, consider citing:

```
@INPROCEEDINGS{hasson19_obman,
  title     = {Learning joint reconstruction of hands and manipulated objects},
  author    = {Hasson, Yana and Varol, G{\"u}l and Tzionas, Dimitris and Kalevatykh, Igor and Black, Michael J. and Laptev, Ivan and Schmid, Cordelia},
  booktitle = {CVPR},
  year      = {2019}
}
```
