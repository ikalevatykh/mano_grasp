import numpy as np
import transforms3d as tf


def mat_rotate_x(alpha):
    ca, sa = np.cos(alpha), np.sin(alpha)
    m = np.matrix([
        [1, 0, 0],
        [0, ca, -sa],
        [0, sa, ca],
    ])
    return m


def mat_rotate_y(beta):
    cb, sb = np.cos(beta), np.sin(beta)
    m = np.matrix([
        [cb, 0, sb],
        [0, 1, 0],
        [-sb, 0, cb],
    ])
    return m


def mat_rotate_z(theta):
    ct, st = np.cos(theta), np.sin(theta)
    m = np.matrix([
        [ct, -st, 0],
        [st, ct, 0],
        [0, 0, 1],
    ])
    return m


def mat_from_rvec(rvec):
    angle = np.linalg.norm(rvec)
    axis = np.array(rvec).reshape(3) / angle if angle != 0 else [0, 0, 1]
    mat = tf.axangles.axangle2mat(axis, angle)
    return np.matrix(mat)


def mat_from_euler(ai, aj, ak, axes='sxyz'):
    mat = tf.euler.euler2mat(ai, aj, ak, axes)
    return np.matrix(mat)


def mat_from_quat(quat):
    x, y, z, w = quat
    mat = tf.quaternions.quat2mat((w, x, y, z))
    return np.matrix(mat)


def rvec_from_mat(mat):
    axis, angle = tf.axangles.mat2axangle(mat, unit_thresh=1e-03)
    rvec = axis * angle
    return rvec


def rvec_from_quat(quat):
    x, y, z, w = quat
    axis, angle = tf.quaternions.quat2axangle((w, x, y, z),
                                              identity_thresh=1e-06)
    rvec = axis * angle
    return rvec


def quat_from_mat(mat):
    w, x, y, z = tf.quaternions.mat2quat(mat)
    return (x, y, z, w)
