from graspit_process import GraspitProcess
from graspit_scene import GraspitScene
from kinematics import Kinematics
from grasp_utils import *


class GraspMiner:
    """ Grasp generator """

    def __init__(self,
                 graspit_process,
                 max_steps=0,
                 max_grasps=0,
                 relax_fingers=False,
                 change_speed=False):
        """Constructor
        
        Arguments:
            graspit_process {GraspitProcess} -- process
        
        Keyword Arguments:
            max_steps {int} -- max search steps per object (default: {auto})
            max_grasps {int} -- return only N best grasps per object (default: {auto})
            change_speed {bool} -- try several joint's speed ratios (default: {False})
            relax_fingers {bool} -- randomize angles of squezzed fingers (default: {False})
        """
        self._process = graspit_process
        self._max_steps = max_steps
        self._max_grasps = max_grasps
        self._relax_fingers = relax_fingers
        self._robot_names = ['ManoHand']
        # we can't change a joints speed ratios on the fly, so use several hand models
        if change_speed:
            self._robot_names += ['ManoHand_v2', 'ManoHand_v3']

    def __call__(self, object_name):
        """Generated grasps for specific object
        
        Arguments:
            object_name {str} -- object
        
        Returns:
            tuple -- object_name, generated grasps
        """
        if not self._process.run:
            self._process.start()

        grasps_all = []
        for robot_name in self._robot_names:
            # load hand and body
            scene = GraspitScene(self._process.graspit, robot_name, object_name)

            # plan grasps with a standart procedure
            plans = scene.planGrasps(max_steps=self._max_steps)

            # execute grasps with different euristics
            variants = (
                dict(approach=False, auto_open=False),  #
                dict(approach=False, auto_open=True, full_open=True),
                dict(approach=True, auto_open=True, full_open=False),
                dict(approach=True, auto_open=True, full_open=True))

            grasps = []
            for plan in plans:
                pose = plan['pose']
                dofs = plan['dofs']

                for args in variants:
                    grasp = scene.grasp(pose, dofs, object_name, **args)
                    if grasp is not None:
                        grasps.append(grasp)

            # sort by quality
            grasps.sort(key=lambda g: g['quality'], reverse=True)

            # cut best grasps
            if self._max_grasps > 0:
                grasps = grasps[:self._max_grasps]

            # GraspIt has a tendency to squeeze the fingers even
            # they aren't in contact with an object.
            # Below we randomize joints positions in such case
            if self._relax_fingers:
                rs = np.random.RandomState(0)
                for i, joints in squeezed(grasps):
                    pose = grasps[i]['pose']
                    dofs = list(grasps[i]['dofs'])
                    for attempt in range(20):
                        angles = rs.uniform(0.0, 2.0, size=len(joints))
                        for j, a in zip(joints, angles):
                            dofs[j] = a
                        grasp = scene.grasp(pose, dofs, object_name)
                        if grasp is not None:
                            grasps[i]['dofs'] = tuple(dofs)

            grasps_all.extend(grasps)

        return (object_name, grasps_all)
