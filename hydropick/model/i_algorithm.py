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

    def process_line(self, survey_line, *args, **kw):
        """ Process a line, returning an array of depths and trace_num's

        trace_num array will be used to define the trace numbers on which the
        line is created (ie use to get the x axis).
        
        return trace_num_array, depth_array
        """
        raise NotImplementedError
