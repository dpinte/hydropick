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

from traits.api import provides, Str, HasTraits, Float
from traitsui.api import View, Item, TextEditor, Group, UItem, Label

from .i_algorithm import IAlgorithm


ALGORITHM_LIST = [
    'ZeroAlgorithm',
    'OnesAlgorithm',
    'XDepthAlgorithm'
]


def create_view(instructions, *args):
    ''' creates a default configuration dialog view for the user to read what
    the algorithm does, and if arguments, what they are, and widgits to set
    them.
    The instructions will be printed readonly at the top of the dialog.
    The arguments will be stacked vertically below using their default editors
    Creator of an algorith can use this as a model to override the configure
    dialog by setting the traits_view trait to a View object similar to this
    '''

    view = View(Group(
                Label('Instructions:', emphasized=True),
                UItem('instructions', editor=TextEditor(), style='readonly',
                      emphasized=True)
                ),
                Item('_'),
                *args,
                buttons=['OK', 'Cancel'],
                kind='modal'
                )
    return view


@provides(IAlgorithm)
class ZeroAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """
    #: a user-friendly name for the algorithm
    name = Str('zeros algorithm')

    # list of names of traits defined in this class that the user needs
    # to set when the algorithm is applied
    arglist = []

    # instructions for user (description of algorithm and required )
    instructions = Str('Demo algorithm that creates a depth line at 0')

    # args (none for this algorithm)

    def process_line(self, survey_line, *args, **kw):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        trace_array = survey_line.trace_num
        zeros_array = np.zeros_like(trace_array)
        return trace_array, zeros_array

    traits_view = create_view(instructions, *arglist)


@provides(IAlgorithm)
class OnesAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """
    #: a user-friendly name for the algorithm
    name = Str('ones algorithm')

    # list of names of traits defined in this class that the user needs
    # to set when the algorithm is applied
    arglist = []

    # instructions for user (description of algorithm and required )
    instructions = Str('Demo algorithm that creates a depth line at 1')

    # args (none for this algorithm)

    def process_line(self, survey_line, *args, **kw):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        trace_array = survey_line.trace_num
        depth_array = np.ones_like(trace_array)
        return trace_array, depth_array

    traits_view = create_view(instructions, *arglist)


@provides(IAlgorithm)
class XDepthAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """

    #: a user-friendly name for the algorithm
    name = Str('x depth algorithm')

    # list of names of traits defined in this class that the user needs
    # to set when the algorithm is applied
    arglist = ['depth']

    # instructions for user (description of algorithm and required )
    instructions = Str('Demo algorithm that creates a depth line at' +
                       ' a depth set by user (defalut = 3.0)\n' +
                       'depth = float')

    # args (none for this algorithm)
    depth = Float(3.0)

    def process_line(self, survey_line):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """
        depth = self.depth
        trace_array = survey_line.trace_num
        depth_array = depth * np.ones_like(trace_array)
        return trace_array, depth_array

    traits_view = create_view(instructions, *arglist)
