#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import
import logging

from shapely.geometry import LineString

from . import hdf5
from ..model.depth_line import DepthLine
from ..model.survey_line import SurveyLine
from ..model.lake import Lake

logger = logging.getLogger(__name__)


def import_survey_line_from_file(filename, h5file, linename):
    hdf5.HDF5Backend(h5file).import_binary_file(filename)


def import_core_samples_from_file(filename, h5file):
    logger.info("Importing corestick file '%s'", filename)
    hdf5.HDF5Backend(h5file).import_corestick_file(filename)


def import_pick_line_from_file(filename, h5file):
    hdf5.HDF5Backend(h5file).import_pick_file(filename)


def import_shoreline_from_file(lake_name, filename, h5file):
    logger.info("Importing shoreline file '%s'", filename)
    hdf5.HDF5Backend(h5file).import_shoreline_file(lake_name, filename)


def read_core_samples_from_hdf(h5file):
    return hdf5.HDF5Backend(h5file).read_core_samples()


def read_shoreline_from_hdf(h5file):
    shoreline_dict = hdf5.HDF5Backend(h5file).read_shoreline()
    return Lake(
        crs=shoreline_dict['crs'],
        name=shoreline_dict['lake_name'],
        shoreline=shoreline_dict['geometry'],
        _properties=shoreline_dict['properties'],
    )


def read_survey_line_from_hdf(h5file, name):
    coords = hdf5.HDF5Backend(h5file).read_survey_line_coords(name)
    line = SurveyLine(name=name,
                      data_file_path=h5file,
                      navigation_line=LineString(coords))
    return line


def read_frequency_data_from_hdf(h5file, name):
    return hdf5.HDF5Backend(h5file).read_frequency_data(name)


def read_sdi_data_unseparated_from_hdf(h5file, name):
    return hdf5.HDF5Backend(h5file).read_sdi_data_unseparated(name)


def read_pick_lines_from_hdf(h5file, line_name, line_type):
    pick_lines = hdf5.HDF5Backend(h5file).read_picks(line_name, line_type)

    return dict([
        (name, DepthLine(**pick_line))
        for name, pick_line in pick_lines.iteritems()
    ])
