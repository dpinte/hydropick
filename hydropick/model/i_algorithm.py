#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Interface, Str

class IAlgorithm(Interface):
    """ An algorithm for detecting features of a survey line

    Classes which implement this interface will likely have a lot of
    user-settable configuration attributes.

    """

    #: a user-friendly name for the algorithm
    name = Str

    def process_line(self, survey_line):
        """ Process a line, returning an array of depths """
        raise NotImplementedError
