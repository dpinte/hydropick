#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Interface, Float, Tuple, List, Str

class ICoreSample(Interface):
    """ An interface representing a core sample """

    #: the core identifier
    core_id = Str

    #: the location of the core sample in easting/northing
    location = Tuple(Float, Float)

    #: the depths of the layer boundaries measured from lake bottom
    layer_boundaries = List # Array?

    # XXX metadata is color and width for each layer, rather than descriptive...
