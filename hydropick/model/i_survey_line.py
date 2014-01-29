#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from shapely.geometry import LineString

from traits.api import (Interface, Array, Dict, Event, Instance, List, Supports,
                        CFloat, Str)

from .i_core_sample import ICoreSample


class ISurveyLine(Interface):
    """ A class representing a single survey line """

    #: the user-visible name for the line
    name = Str

    #: file location for this surveyline.  Used to load data when needed.
    data_file_path = Str

    #: sample locations, an Nx2 array (example: easting/northing?)
    locations = Array(shape=(None, 2))

    #: specifies unit for values in locations array
    locations_unit = Str

    #: array of associated lat/long available for display
    lat_long = Array(shape=(None, 2))

    #: a dictionary mapping frequencies to intensity arrays
    frequencies = Dict

    #: relevant core samples
    core_samples = List(Supports(ICoreSample))

    #: depth of the lake at each location as generated by various soruces
    lake_depths = Dict(Str, Array)

    # and event fired when the lake depths are updated
    lake_depths_updated = Event

    #: The navigation track of the survey line in map coordinates
    navigation_line = Instance(LineString)

    #: pre-impoundment depth at each location as generated by various soruces
    preimpoundment_depths = Dict(Str, Array)

    # and event fired when the lake depth is updated
    preimpoundment_depths_updated = Event

    ##: Depth corrections:
    ##:     depth = (pixel_number_from_top * pixel_resolution) + draft - heave

    #: distance from sensor to water. Constant offset added to depth
    draft = CFloat

    #: array of depth corrections to vertical offset of each column (waves etc)
    heave = Array

    #: pixel resolution, depth/pixel
    pixel_resolution = CFloat

    # XXX probably other metadata should be here
