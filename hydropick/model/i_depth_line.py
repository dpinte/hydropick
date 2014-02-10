#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Interface, Str, Enum, Array, Bool, Color, Dict


class IDepthLine(Interface):
    """ An interface representing a depth line

    Each depth line is associated with a specific survey line.
    It can have an arbitrary number of points whose indices are a subset
    of the combined interleaved set of trace numbers.
    """

    #: the name of the survey line this depth line belongs to
    survey_line_name = Str

    #: name given to this line
    name = Str

    #: line type
    line_type = Enum('current surface', 'pre-impoundment surface')

    #: source of the line's depth data
    source = Enum('algorithm', 'previous depth line', 'sdi_file', 'manual')

    #: name of source: like name of algorithm or source line to look up source
    source_name = Str

    #: arguments for the source: typically arguments to be sent to an algorithm
    args = Dict

    #: array of indices (trace_num's) on which the line is defined
    index_array = Array

    # array of depth values for each index
    depth_array = Array

    # indicated line was manually edited.  Source should indicate original line
    edited = Bool

    #: display color for line (should not be same color as selected edit line)
    color = Color

    #: text field for any notes about this line.
    notes = Str

    # lock prevents depth line from being edited.
    lock = Bool
