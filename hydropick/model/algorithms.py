#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import numpy as np

from traits.api import provides, Str, HasTraits


from .i_algorithm import IAlgorithm

ALGORITHM_LIST = [
    'ZeroAlgorithm'
]

@provides(IAlgorithm)
class ZeroAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """

    #: a user-friendly name for the algorithm
    name = Str('zeros algorithm')

    def process_line(self, survey_line):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        N = survey_line.shape[1]
        return np.zeros(N)
