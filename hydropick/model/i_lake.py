#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Any, Dict, Instance, Interface, Float, Str
from scimath import units


class ILake(Interface):
    """ The interface for an object representing a lake """

    #### 'ILake' protocol #################################################

    #: Name of the lake
    name = Str

    #: The coordinate reference system as a pyproj dictionary mapping
    crs = Dict

    #: Elevation (in elevation_units)
    elevation = Float

    #: Units for elevation
    elevation_units = Instance(units.unit.unit)

    #: The geometry of the shoreline.
    shoreline = Any
