import numpy as np
import os
import subprocess
import uuid
from threading import Timer

import rospy
from rospy.exceptions import ROSException


class GraspitProcess:
    """ GraspIt process wrapper

    Run a GraspIt instance in a separate process and setup 
    a GraspitCommander to communicate with it using ROS.

    """

    def __init__(self,
                 graspit_dir='',
                 plugin_dir='',
                 headless=False,
                 xvfb_run=False,
                 verbose=False):
        """Constructor
        
        Keyword Arguments:
            graspit_dir {str} -- path to GraspIt root directory  (default: {auto})
            plugin_dir {str} -- path to directory with a graspit_interface plugin  (default: {auto})
            headless {bool} -- start GraspIt in headless mode (default: {False})
            xvfb_run {bool} -- use Xserver Virtual Frame Buffer (Xvfb) (default: {False})
            verbose  {bool} -- echoing GraspIt output to console (default: {False})
        """
        self._graspit_dir = graspit_dir or os.environ['GRASPIT']
        self._plugin_dir = plugin_dir or os.environ['GRASPIT_PLUGIN_DIR']
        self._headless = headless or xvfb_run
        self._xvfb_run = xvfb_run
        self._verbose = verbose
        self._run = False
        self._uid = None
        self._proc = None
        self._node_name = None
        self._commander = None

    @property
    def graspit(self):
        """ GraspitCommander associated with this GraspIt instance """
        return self._commander

    @property
    def dir(self):
        """ Path to GraspIt root directory """
        return self._graspit_dir

    def _startProcess(self):
        uid = uuid.uuid1().hex
        graspit_node_name = 'graspit_{}'.format(uid)
        devnull = open(os.devnull, 'wb')

        proc = subprocess.Popen(
            # yapf: disable
            [
                '{}graspit_simulator'.format('xvfb-run ' if self._xvfb_run else ''), '-p',
                'libgraspit_interface', '--node_name', graspit_node_name,
                '__name:={}'.format(graspit_node_name), '--headless' if self._headless else ''
            ],
            # yapf: enable
            shell=False,
            stdout=None if self._verbose else devnull,
            stderr=None if self._verbose else devnull)

        self._proc = proc
        self._uid = uid
        self._node_name = graspit_node_name

    def _setupCommander(self):
        uid = self._uid
        commander_node_name = 'GraspItCommanderNode_{}'.format(uid)
        from graspit_commander import GraspitCommander
        GraspitCommander.ROS_NODE_NAME = commander_node_name
        GraspitCommander.GRASPIT_NODE_NAME = '/' + self._node_name + '/'
        try:
            rospy.wait_for_service('/' + self._node_name + '/clearWorld', timeout=15.0)
        except ROSException, e:
            retcode = self._proc.poll()
            raise Exception('Cannot connect to a graspit node, process retcode: ', retcode)
        self._commander = GraspitCommander

    @property
    def run(self):
        return self._run

    def start(self):
        assert self._run == False
        self._startProcess()
        self._setupCommander()
        self._run = True

    def join(self, timeout=5.0):
        if self._proc is not None:
            self._proc.terminate()
            timer = Timer(timeout, self._proc.kill)
            try:
                timer.start()
                self._proc.communicate()
            finally:
                timer.cancel()
                self._proc = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.join()

    def __del__(self):
        self.join()

    def __repr__(self):
        return "GraspIt process: {}".format(self._uid)