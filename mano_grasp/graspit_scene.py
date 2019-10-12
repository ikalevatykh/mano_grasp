import os
from geometry_msgs.msg import Pose

from kinematics import Kinematics
from grasp_utils import *


class GraspitScene:
    """ Scene with a hand (robot) and a body """

    def __init__(self, graspit, robot, body):
        default_pose = Pose()
        default_pose.position.y = 0.2
        default_pose.orientation.w = 1

        graspit.clearWorld()
        graspit.importRobot(robot)
        graspit.setRobotPose(default_pose)
        graspit.importGraspableBody(body)

        self._graspit = graspit
        self._robot = robot
        self._body = body
        self._kinematics = Kinematics('{}/models/robots/{}'.format(os.environ['GRASPIT'], robot))

    def planGrasps(self, max_steps=70000):
        """Plan grasps
        
        Keyword Arguments:
            max_steps {int} -- planner max steps (default: {70000})
        
        Returns:
            list -- list of planned grasps
        """
        result = self._graspit.planGrasps(max_steps=max_steps)
        return [grasp_from_msg(g) for g in result.grasps]

    def grasp(self, pose, dofs, body='', approach=False, auto_open=False, full_open=False):
        """Execute a grasp
        
        Arguments:
            pose {list} -- hand root position
            dofs {list} -- hand dofs angles
            body {str} -- grasping body name
            approach {bool} -- approch to contact before close fingers
            auto_open {bool} -- open fingers before closing
            full_open {bool} -- disable collision checking while opening
        
        Returns:
            dict -- grasp data
        """
        graspit = self._graspit
        kinematics = self._kinematics
        try:
            # execute grasp
            graspit.toggleAllCollisions(False)
            graspit.setRobotPose(msg_from_pose(pose))
            graspit.forceRobotDof(dofs)
            if auto_open:
                if not full_open:
                    graspit.toggleAllCollisions(True)
                graspit.autoOpen()
            graspit.toggleAllCollisions(True)
            if approach:
                graspit.approachToContact()
            graspit.autoGrasp()
            # compute quality
            quality = graspit.computeQuality()
            if quality.result == 0 and quality.epsilon > -1:
                response = graspit.getRobot()
                robot = response.robot
                return grasp_from_robot_state(robot, quality, body, kinematics)
        except Exception:
            pass

    def __repr__(self):
        return "Scene {} -> {}".format(self._robot, self._body)