# -*- coding: utf-8 -*-
"""
Created on Thu May 15 19:51:33 2014

@author: Yuxiang Wang
"""


import numpy as np


def get_loadcell_param():
    """
    Get the line fit for loadcell calibration. Units are ISO.
    """
    grams_array = np.array([0, 32.4, 48.6, 72.8, 95.9])
    volts_array = np.array([-1.1993, 1.2614, 2.5546, 4.4014, 6.2026])
    newtons_list = grams_array * 1e-3 * 9.8
    loadcell_param = np.polyfit(volts_array, newtons_list, 1)
    return loadcell_param


LC = get_loadcell_param()
XPS_IP = '192.168.0.254'
GROUPNAME = 'GROUP1'
POSITIONER = GROUPNAME + '.POSITIONER'
FORCE_SENSOR = 'GPIO2.ADC1'
MIN_JERK_TIME = .005
MAX_JERK_TIME = .05
TIME_PAD = .5
