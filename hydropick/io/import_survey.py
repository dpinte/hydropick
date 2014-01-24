#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import os
import logging

import numpy as np
from shapely.geometry import LineString

logger = logging.getLogger(__name__)

# XXX this is not fully implemented

def get_name(directory):
    # name defaults to parent and grandparent directory names
    directory = os.path.abspath(directory)
    parent, dirname = os.path.split(directory)
    grandparent, parent_name = os.path.split(parent)
    great_grandparent, grandparent_name = os.path.split(grandparent)
    if parent_name and grandparent_name:
        name = grandparent_name + ' ' + parent_name
    elif parent_name:
        name = parent_name
    else:
        name = "Untitled"
    return name

def import_cores(directory):
    from sdi import corestick
    from ..model.core_sample import CoreSample

    cores = []
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1] == '.txt':
            # this is a corestick file
            logger.info("Reading corestick file '%s'", filename)
            for core_id, core in corestick.read(os.path.join(directory, filename)).items():
                core_sample = CoreSample(
                    core_id=core_id,
                    location=(core['easting'], core['northing']),
                    layer_boundaries=core['layer_interface_depths'],
                )
                cores.append(core_sample)
    return cores


def import_lake(directory):
    # XXX this needs a proper implementation
    from ..model.lake import Lake

    # find the GIS file in the directory
    for filename in os.listdir(directory):
        if os.path.splitext(filename)[1] == '.shp':
            return Lake(shoreline_file=os.path.join(directory, filename))
    pass


def import_sdi(directory, h5file):
    import tables
    from sdi import binary
    from ..model.survey_line import SurveyLine
    from ..model.survey_line_group import SurveyLineGroup

    survey_lines = []
    survey_line_groups = []
    for root, dirs, files in os.walk(directory):
        group_lines = []
        for filename in files:
            if os.path.splitext(filename)[1] == '.bin':
                linename = os.path.splitext(filename)[0]
                print 'Reading line', linename
                try:
                    with tables.openFile(h5file, 'r') as f:
                        coords = f.getNode('/l' + linename + '/navigation_line').read()
                except (IOError, tables.exceptions.NoSuchNodeError):
                    logger.info("Reading sdi file '%s'", filename)
                    try:
                        data = binary.read(os.path.join(root, filename))
                    except:
                        # XXX: blind except to read all the lines that we can for now
                        print 'Failed!'
                        break
                    x = data['frequencies'][-1]['easting']
                    y = data['frequencies'][-1]['northing']
                    coords = np.vstack((x, y)).T
                    with tables.openFile(h5file, 'a') as f:
                        node = f.createGroup(f.root, 'l' + linename)
                        f.createArray('/l' + linename, 'navigation_line', coords)
                        # TODO: write frequency arrays to datastore
                line = SurveyLine(
                    name=linename,
                    navigation_line=LineString(coords),
                    #frequencies=data['frequencies'],
                )
                group_lines.append(line)
        if group_lines:
            dirname = os.path.basename(root)
            group = SurveyLineGroup(name=dirname, survey_lines=group_lines)
            survey_lines += group_lines
            survey_line_groups.append(group)
    return survey_lines, survey_line_groups


def import_survey(directory):
    """ Read in a project from the current directory-based format """
    from ..model.survey import Survey

    name = get_name(directory)

    # read in core samples
    core_samples = import_cores(os.path.join(directory, 'Coring'))

    # read in lake
    lake = import_lake(os.path.join(directory, 'ForSurvey'))

    # HDF5 datastore file for survey
    hdf5file = os.path.join(directory, name + '.h5')
    print hdf5file

    # read in sdi data
    survey_lines, survey_line_groups = import_sdi(os.path.join(directory, 'SDI_Data'),
                                                  hdf5file)

    # read in edits to sdi data
    # XXX not implemented

    survey = Survey(
        name=name,
        lake=lake,
        survey_lines=survey_lines,
        survey_line_groups=survey_line_groups,
        core_samples=core_samples,
    )

    return survey
