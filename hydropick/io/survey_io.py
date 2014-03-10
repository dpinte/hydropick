#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import
import logging
import numpy as np

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

def write_depth_line_to_hdf(h5file, depth_line, survey_line_name):
    d = depth_line
    data = dict(
        name=d.name,
        survey_line_name=d.survey_line_name,
        line_type=d.line_type,
        source=d.source,
        source_name=d.source_name,
        args=d.args,
        index_array=d.index_array,
        depth_array=d.depth_array,
        edited=d.edited,
        color=str(d.color.toTuple()),
        notes=d.notes,
        lock=d.lock,
    )
    if d.line_type == 'current surface':
        line_type = 'current'
    else:
        line_type = 'preimpoundment'
    hdf5.HDF5Backend(h5file).write_pick(data, survey_line_name, line_type)

def check_trace_num_array(trace_num_array, survey_line_name):
    ''' checks for bad points in trace_num array.
    assumes trace num array should be a sequential array, 1 to len(array)
    (as specified in sdi.binary).  Returns bad trace numbers and bad values
    this should be done when loading survey line arrays and associated depth
    lines.
    '''
    ref = np.arange(len(trace_num_array)) + 1
    # this returns index for any traces that don't match ref
    bad_indices = np.nonzero(trace_num_array - ref)[0]
    bad_values = trace_num_array[bad_indices]
    if bad_indices:
        # log the problem
        s = '''trace_num not contiguous for array: {}.
        values of {} at traces {}
        '''.format('name', bad_values, bad_indices + 1)
        logger.warn(s)
    
    return bad_indices, bad_values

def fix_trace_num_arrays(trace_num_array, bad_indices, freq_trace_num):
    ''' Replaces bad trace num values with the appropriate sequential value,
    then fixes main trace num_array
    This should really be done in sdi binary read but for now this is a fix.
    '''
    for freq, trace_array in freq_trace_num.items():
        # find the trace num indices in the freq trace num subset
        indices_in_freq = np.where(np.in1d(trace_num_array, trace_array))[0]
        # get trace num indices of bad traces in this freq_trace_num array
        bad_in_freq = bad_indices[np.in1d(bad_indices, indices_in_freq)]
        for index in bad_in_freq:
            # find the index in freq trace num where this index should go
            i_in_freq = np.searchsorted(indices_in_freq, index)
            # set the value to correct trace number which is the index + 1
            trace_array[i_in_freq] = index + 1
    trace_num_array = np.arange(1, len(trace_num_array) + 1)
    
    return trace_num_array, freq_trace_num
        
            
        
    
    
    
