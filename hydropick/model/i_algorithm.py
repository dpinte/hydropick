#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Interface, Str, Any


class IAlgorithm(Interface):
    """ An algorithm for detecting features of a survey line

    Classes which implement this interface will likely have a lot of
    user-settable configuration attributes.

    """

    #: a user-friendly name for the algorithm
    name = Str
    
    # list of names of traits defined in this class that the user needs
    # to set when the algorithm is applied
    arglist = []

    # instructions for user (description of algorithm and required args def)
    instructions = Str()

    def process_line(self, survey_line, *args, **kw):
        """ Process a line, returning an array of depths and trace_num's

        trace_num array will be used to define the trace numbers on which the
        line is created (ie use to get the x axis).
        
        return trace_num_array, depth_array
        """
        raise NotImplementedError

    # should be a View object or somthing that returns a view object for
    # configuring the arguments in arglist and displaying instructions
    traits_view = Any
