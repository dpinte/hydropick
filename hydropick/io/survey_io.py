#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import numpy as np
from shapely.geometry import LineString
import tables

from sdi import binary
from . import hdf5
from ..model.survey_line import SurveyLine


def import_survey_line_from_file(filename, h5file, linename):
    hdf5.HDF5Backend(h5file).import_binary_file(filename)

def read_survey_line_from_hdf(h5file, name):
    coords = hdf5.HDF5Backend(h5file).read_survey_line_coords(name)
    line = SurveyLine(name=name,
                      data_file_path=h5file,
                      navigation_line=LineString(coords))
    return line


def read_frequency_data_from_hdf(h5file, name):
    return hdf5.HDF5Backend(h5file).read_frequency_data(name)
