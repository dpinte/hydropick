#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import os

import numpy as np
from shapely.geometry import LineString
import tables

from sdi import binary
from ..model.survey_line import SurveyLine

def read_survey_line_from_file(filename, linename):
    data = binary.read(filename)
    x = data['frequencies'][-1]['easting']
    y = data['frequencies'][-1]['northing']
    coords = np.vstack((x, y)).T
    line = SurveyLine(name=linename,
                      data_file_path=filename,
                      navigation_line=LineString(coords))
    return line

def read_survey_line_from_hdf(h5file, name):
    with tables.openFile(h5file, 'r') as f:
        coords = f.getNode('/l' + name + '/navigation_line').read()
    line = SurveyLine(name=name,
                      navigation_line=LineString(coords))
    return line

def write_survey_line_to_hdf(h5file, line):
    coords = np.vstack(line.navigation_line.coords.xy)
    with tables.openFile(h5file, 'a') as f:
        node = f.createGroup(f.root, 'l' + line.name)
        f.createArray('/l' + line.name, 'navigation_line', coords.T)
        # TODO: write frequency arrays to datastore
