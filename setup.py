#!/usr/bin/env python2

import argparse
import os
import sys

from distutils.core import setup
from distutils.dir_util import copy_tree

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--copy_model_only',
                    action='store_true',
                    help="Just copy MANO model to GraspIt robots directory")
parser.add_argument('--graspit_dir',
                    type=str,
                    default=os.environ['GRASPIT'],
                    help="Path to GraspIt root directory")


def copy_model(args):
    """Copy hand model to GraspIt model's directory"""

    model_name = 'ManoHand'
    source_dir = os.path.join('models', model_name)
    target_dir = os.path.join(args.graspit_dir, 'models', 'robots', model_name)

    if not os.path.isdir(target_dir):
        copy_tree(source_dir, target_dir)

    for ver in ['v2', 'v3']:
        source = target_dir
        target = target_dir + '_{}'.format(ver)
        if not os.path.islink(target):
            print('Create symlink "{}" -> "{}"'.format(source, target))
            os.symlink(source, target)


def setup_package():
    """Setup package"""

    with open("./requirements.txt", "r") as f:
        requirements = [l.strip() for l in f.readlines() if len(l.strip()) > 0]

    setup(name='mano_grasp',
          version='1.0',
          description='Grasps generation for the MANO model in GraspIt',
          author='Igor Kalevatykh',
          author_email='igor.kalevatykh@inria.fr',
          url='https://hassony2.github.io/obman',
          packages=['mano_grasp'],
          requires=requirements)


if __name__ == '__main__':
    parseable_args = []
    unparseable_args = []
    for i, arg in enumerate(sys.argv):
        if arg == "--":
            unparseable_args = sys.argv[i:]
            break
        parseable_args.append(arg)

    args, filtered_args = parser.parse_known_args(args=parseable_args)
    sys.argv = filtered_args + unparseable_args

    if not args.copy_model_only:
        setup_package()
    copy_model(args)