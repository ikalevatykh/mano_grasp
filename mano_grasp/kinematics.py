import collections
import json
import numpy as np
import os

from math_utils import *

CHAIN_NAME = collections.OrderedDict(chain0='index',
                                     chain1='mid',
                                     chain2='ring',
                                     chain3='pinky',
                                     chain4='thumb')


class Kinematics:
    """ Kinematics converter GraspIt -> MANO """

    def __init__(self, path=''):
        """Constructor
        
        Keyword Arguments:
            path {str} -- path to to directory with a kinematics.json (default: {''})
        """
        with open(os.path.join(path, 'kinematics.json'), 'r') as f:
            data = json.load(f)
        fingers = ['index', 'mid', 'pinky', 'ring', 'thumb']
        self._chains = [Chain(n, data) for n in CHAIN_NAME.values()]
        self._origin = data['origin']

    def getManoPose(self, xyz, quat, dofs):
        """Convert a hand pose from GraspIt to MANO
        
        Arguments:
            xyz  -- root position, vector x,y,z
            quat -- root orientation, quaternion x,y,z,w
            dofs -- joint angles, 20-length vector
        
        Returns:
            trans -- MANO hand's translation
            pose  -- MANO hand's pose
        """
        pose = [rvec_from_quat(quat)]
        for chain in self._chains:
            p0 = chain.mano_root_mat
            m0 = chain.solid_root_mat
            m = m0.copy()
            for i in range(4):
                theta = dofs[chain.dof_index[i]] * chain.dof_coeff[i]
                m0i = chain.tau0[i]
                m0 = m0 * m0i
                mi = mat_rotate_z(theta) * m0i
                zi = m * [[0], [0], [1]]
                m = m * mi

                if i == 1:
                    p = m * m0.T * p0
                    rvec = rvec_from_mat(p)
                    pose.append(rvec)
                elif i > 1:
                    axis = np.array(p.T * zi).reshape(3)
                    rvec = axis * theta
                    p = p.dot(mat_from_rvec(rvec))
                    pose.append(rvec)
        pose = np.array(pose).flatten()

        m = mat_from_quat(quat)
        trans = np.array(xyz) - self._origin + np.dot(m, self._origin)

        return trans.tolist(), pose.tolist()


class Chain:

    def __init__(self, name, data):
        self.name = name
        self.solid_root_mat = np.matrix(data['{}_graspit_origin'.format(name)])
        self.mano_root_mat = np.matrix(data['{}_mano_origin'.format(name)])
        self.dof_index = [data['{}_{}_dof_index'.format(name, i)] for i in range(4)]
        self.dof_coeff = [data['{}_{}_dof_coeff'.format(name, i)] for i in range(4)]
        self.tau0 = [np.matrix(data['{}_{}_tau0'.format(name, i)]) for i in range(4)]
