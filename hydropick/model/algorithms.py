#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#
"""
Define algorithm classes following the model and place the class name in the
ALGORITHM_LIST constant at the top.  Each algorithm must have a unique name
string or it will not be recognized.

"""

from __future__ import absolute_import

import numpy as np

from traits.api import provides, Str, HasTraits


from .i_algorithm import IAlgorithm


ALGORITHM_LIST = [
    'ZeroAlgorithm',
    'OnesAlgorithm',
    'XDepthAlgorithm'
]


@provides(IAlgorithm)
class ZeroAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """

    #: a user-friendly name for the algorithm
    name = Str('zeros algorithm')

    def process_line(self, survey_line, *args, **kw):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        trace_array = survey_line.trace_num
        zeros_array = np.zeros_like(trace_array)
        return trace_array, zeros_array


@provides(IAlgorithm)
class OnesAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """

    #: a user-friendly name for the algorithm
    name = Str('ones algorithm')

    def process_line(self, survey_line, *args, **kw):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        trace_array = survey_line.trace_num
        depth_array = np.ones_like(trace_array)
        return trace_array, depth_array

@provides(IAlgorithm)
class XDepthAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """

    #: a user-friendly name for the algorithm
    name = Str('x depth algorithm')

    def process_line(self, survey_line, *args, **kw):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        depth = kw.get('depth', 1)
        trace_array = survey_line.trace_num
        depth_array = depth * np.ones_like(trace_array)
        return trace_array, depth_array
