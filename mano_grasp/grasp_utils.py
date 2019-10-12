import numpy as np
from geometry_msgs.msg import Pose

from kinematics import CHAIN_NAME


def pose_from_msg(msg):
    pos = msg.position
    orn = msg.orientation
    return [pos.x, pos.y, pos.z, orn.x, orn.y, orn.z, orn.w]


def msg_from_pose(pose):
    msg = Pose()
    pos = msg.position
    orn = msg.orientation
    pos.x, pos.y, pos.z, orn.x, orn.y, orn.z, orn.w = pose
    return msg


def vector_from_msg(msg):
    vector = msg.vector
    return [vector.x, vector.y, vector.z]


def contact_from_msg(msg):
    pose = pose_from_msg(msg.ps.pose)
    if msg.body1 == 'Base':
        link = 'palm'
    else:
        parts = msg.body1.split('_')
        chain = CHAIN_NAME[parts[1]]
        link = chain + '_' + parts[2]
    return dict(link=link, pose=pose)


def grasp_from_msg(grasp, kinematics=None):
    return dict(pose=pose_from_msg(grasp.pose),
                dofs=grasp.dofs,
                contacts=[],
                epsilon=grasp.epsilon_quality,
                volume=grasp.volume_quality,
                link_in_contact=[],
                quality=-1)


def grasp_from_robot_state(robot, quality, body_name, kinematics=None):
    contacts = [contact_from_msg(c) for c in robot.contacts if c.body2 == body_name]
    links = list(set([c['link'] for c in contacts]))
    palm_contact = 'palm' in links
    average_quality = np.linalg.norm([quality.epsilon, quality.volume]) \
                      * (3.0 if palm_contact else 1.0) \
                      * (len(links) ** 0.5)
    pose = pose_from_msg(robot.pose)
    dofs = robot.dofs
    grasp = dict(
        body=body_name,
        pose=pose,
        dofs=dofs,
        contacts=contacts,
        epsilon=quality.epsilon,
        volume=quality.volume,
        link_in_contact=links,
        quality=average_quality,
    )

    if kinematics is not None:
        trans, pose = kinematics.getManoPose(pose[:3], pose[3:], dofs)
        grasp.update(dict(mano_trans=trans, mano_pose=pose))

    return grasp


def squeezed(grasps):
    intermadiates = [1, 4, 7, 10, 14]
    distals = [2, 5, 8, 11, 15]
    offsets = np.array([10.5, 6.5, 8, 2.2, 0])
    dependent = [
        set(['index_link1', 'index_link2']),
        set(['mid_link1', 'mid_link2']),
        set(['ring_link1', 'ring_link2']),
        set(['pinky_link1', 'pinky_link2']),
        set(['thumb_link2'])
    ]
    for i, grasp in enumerate(grasps):
        pose = grasp['pose']
        dofs = np.degrees(grasp['dofs'])
        link_in_contact = set(grasp['link_in_contact'])

        squeezed = dofs[distals] + offsets > 94
        no_touch = [not (l & link_in_contact) for l in dependent]
        indicies = np.logical_and(squeezed, no_touch)

        joints = [intermadiates[i] for i, cond in enumerate(indicies) if cond] + \
            [distals[i] for i, cond in enumerate(indicies) if cond]

        if joints:
            yield i, joints
