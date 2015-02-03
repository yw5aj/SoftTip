# -*- coding: utf-8 -*-
"""
Created on Thu May 15 17:02:22 2014

@author: Yuxiang Wang
"""

# General imports
import numpy as np
import time

# Custom imports
from XPS_C8_drivers import XPS
from constants import (XPS_IP, LC, GROUPNAME, POSITIONER, MIN_JERK_TIME,
                       MAX_JERK_TIME, TIME_PAD, FORCE_SENSOR)


class Session:

    def __init__(self, xps_ip=XPS_IP):
        self.xps = XPS()
        self.ip = xps_ip
        self.get_socket_id()
        self.initialize_motion()
        self.get_force_offset()
        return

    def get_socket_id(self):
        self.socket_id = self.xps.TCP_ConnectToServer(self.ip, 5001, 60)
        assert self.socket_id is not -1, 'Connection failed.'
        return self.socket_id

    def get_force_offset(self):
        self.force_offset = 0.
        self.force_offset = np.mean([self.get_current_force() for i in
                                    range(5)])
        return

    def initialize_motion(self):
        self.xps.GroupKill(self.socket_id, GROUPNAME)
        self.xps.GroupInitialize(self.socket_id, GROUPNAME)
        self.xps.GroupHomeSearch(self.socket_id, GROUPNAME)
        return

    def gather_start(self, duration, freq=1e3):
        """
        Gather position and force data for certain duration (sec) at given
        frequency (Hz).
        """
        self.xps.GatheringConfigurationSet(self.socket_id, [
            POSITIONER+'.CurrentPosition', 'GPIO2.ADC1'])
        # System servo cycle frequency is 10 kHz, manual p.137
        divisor = int(10e3 / freq)
        data_number = int(duration * freq)
        self.xps.GatheringRun(self.socket_id, data_number, divisor)
        return

    def get_current_force(self):
        current_force_raw = np.polyval(LC, self.get_current_force_volt())
        current_force = current_force_raw - self.force_offset
        return current_force

    def get_current_force_volt(self):
        force_volt = self.xps.GPIOAnalogGet(self.socket_id, [FORCE_SENSOR])[1]
        return force_volt

    def force2volt(self, force):
        """
        Unit of the force in N.
        """
        raw_force = force + self.force_offset
        volt = (raw_force - LC[1]) / LC[0]
        return volt

    def get_current_displ(self):
        current_displ = self.xps.GroupPositionCurrentGet(
            self.socket_id, GROUPNAME, 1)[1]
        return current_displ

    def gather_get_data(self, freq=1e3, save_data=True):
        data_number = self.xps.GatheringCurrentNumberGet(self.socket_id)[1]
        data_list = []
        for i in range(data_number):
            data_list.append(np.fromstring(self.xps.GatheringDataGet(
                self.socket_id, i)[1], sep=';'))
        displ_array, force_array = np.array(data_list).T
        # Convert the force from volts to newtons
        force_array = np.polyval(LC, force_array)
        time_array = np.arange(force_array.size) / freq
        if save_data:
            fname = time.strftime('./csvs/%Y%m%d%H%M%S.csv', time.localtime())
            np.savetxt(fname, np.c_[time_array, displ_array, force_array],
                       delimiter=',')
        return time_array, displ_array, force_array

    def move_rel(self, displ, vel, acc=40.):
        """
        Move the indenter tip using displacement controlled mode. Units based
        on mm and s.
        """
        self.xps.PositionerSGammaParametersSet(
            self.socket_id, POSITIONER, vel, acc, MIN_JERK_TIME, MAX_JERK_TIME)
        self.xps.GroupMoveRelative(self.socket_id, GROUPNAME, [displ])
        return

    def move_abs(self, displ, vel, acc=40.):
        self.xps.PositionerSGammaParametersSet(
            self.socket_id, POSITIONER, vel, acc, MIN_JERK_TIME, MAX_JERK_TIME)
        self.xps.GroupMoveAbsolute(self.socket_id, GROUPNAME, [displ])
        return

    def find_force_pos(self, force):
        while self.get_current_force() < force:
            self.move_rel(0.01, 1.)
        return self.get_current_displ()

    def displ_ramp_hold(self, displ, vel, hold_duration, freq=1e3):
        ramp_duration = displ / vel
        data_duration = ramp_duration + hold_duration + TIME_PAD
        # Start collecting data
        self.gather_start(data_duration, freq=freq)
        # Move the indenter
        self.move_rel(displ, vel)
        # Hold on for hold_duration
        time.sleep(hold_duration)
        # Lift the indenter
        self.move_rel(-displ, 40)
        # Collect gathered data
        time_array, displ_array, force_array = self.gather_get_data(freq=freq)
        return time_array, displ_array, force_array


if __name__ == '__main__':
    session = Session()

    def diagnose(i):
        while True:
            print(session.xps.GPIOAnalogGet(session.socket_id,
                                            ['GPIO2.ADC%d' % i])[1])
            time.sleep(0.3)
        return
    diagnose(2)
