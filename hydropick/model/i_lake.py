#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from traits.api import Interface, Str

class ILake(Interface):
    """ The interface for an object representing a lake """

    name = Str

    # XXX this should have things like the map outline coordinates, projections,
    # and other metadata about the lake itself
