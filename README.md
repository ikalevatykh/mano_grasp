# Learning Joint Reconstruction of Hands and Manipulated Objects - ManoGrasp

Porting the MANO hand model to GraspIt simulator

Yana Hasson, Gül Varol, Dimitris Tzionas, Igor Kalevatykh, Michael J. Black,  Ivan Laptev, Cordelia Schmid, CVPR 2019

- [Project page](https://hassony2.github.io/obman)

## Install

```
git clone https://github.com/ikalevatykh/mano_grasp.git
cd mano_grasp
python setup.py install --user --graspit_dir=$GRASPIT
```

## Model

Model ManoHand will be automatically copied to $GRASPIT directory.

## Generate grasps

    python -m mano_grasp.generate_grasps --path_out PATH_TO_DATASET

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
