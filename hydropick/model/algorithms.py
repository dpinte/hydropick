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

from scipy.signal import medfilt
from sklearn.mixture import GMM
from skimage.morphology import binary_opening, disk

from traits.api import provides, Str, HasTraits, Float, Range
from traitsui.api import View, Item, TextEditor, Group, UItem, Label

from .i_algorithm import IAlgorithm


ALGORITHM_LIST = [
    'ZeroAlgorithm',
    'OnesAlgorithm',
    'XDepthAlgorithm',
    'CurrentSurface',
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
class CurrentSurface(HasTraits):
    """ Algorithm to pick current surface from 200Khz Intensity Image

    """

    #: a user-friendly name for the algorithm
    name = Str('Current Surface Algorithm')

    # list of names of traits defined in this class that the user needs
    # to set when the algorithm is applied
    arglist = ['weight']

    # instructions for user (description of algorithm and required args def)
    instructions = Str('Algorith to autodetect current surface from ' +
                       ' 200kHz intensity image. \n' +
                       'weight = 0.0 - 1.0 (default = 0.67)')

    # args
    weight = Range(value=0.67, low=0.0, high=1.0)

    def process_line(self, survey_line):
        """ returns all zeros to provide a blank line to edit.
        Size matches horizontal pixel number of intensity arrays
        """

        # aaargh! ok this is the whole reason we don't want floats as dict keys
        freq = str(max([float(k) for k in survey_line.frequencies.keys()]))

        trace_array = survey_line.trace_num
        trace_array_200 = survey_line.freq_trace_num[freq]

        #idx_200khz = np.max(survey_line.frequencies.keys())
        intensity_200 = survey_line.frequencies[freq].copy()
        #fill nans with median value
        intensity_200[np.isnan(intensity_200)] = np.median(intensity_200)

        depth_array = np.empty(len(trace_array))
        depth_array.fill(np.nan)
        depth_array[trace_array_200-1] = self._find_edge(intensity_200)

        depth_array = self._interpolate_nans(depth_array) * survey_line.pixel_resolution 
        depth_array += survey_line.draft - survey_line.heave

        return trace_array, depth_array


    def _find_top_bottom(self, img, buf=5):
        x = np.mean(img, axis=1)
        classif = GMM(n_components=2, covariance_type='full')
        fit = classif.fit(x.reshape((x.size, 1)))
        bot = np.where(x > fit.means_.min())[0][-1]+buf      
        top = np.where(x < fit.means_.mean())[0][0]
        try:
            fit.fit(x[top:top+100].reshape((x[top:top+100].size, 1)))
            top += np.where(x[top:top+100] < fit.means_.min())[0][0]
        except:
            top += buf

        return top, bot, fit

    def _last_point(self, x, p):
        x = np.where(x[:p])[0]
        if len(x) > 0:
            return x[-1]
        else:
            return np.nan

    def _find_edge(self, img, buf=5, weight=weight):
        top, bot, fit = self._find_top_bottom(img, buf)
        clip = img[top:bot, :]
        a, b = fit.means_.min(), fit.means_.max()
        threshold = a + weight*(b-a)
        binary_img = img < threshold
        #remove small speckles
        binary_img = binary_opening(binary_img, disk(3))
        centers = medfilt(np.argmax(clip, axis=0), kernel_size=9).astype(np.int) + top
        cur_pics = 1.0*np.empty_like(centers)
        cur_pics.fill(np.nan)

        for i in range(len(centers)):
            cur_pics[i] = self._last_point(binary_img[:, i], centers[i])

        return cur_pics

    def _interpolate_nans(self, y):
        nans, x = np.isnan(y), lambda z: z.nonzero()[0]
        y[nans] = np.interp(x(nans), x(~nans), y[~nans])
        return y.round(0).astype(np.int)

    traits_view = create_view(instructions, *arglist)



@provides(IAlgorithm)
class ZeroAlgorithm(HasTraits):
    """ A default algorithm for testing or hand drawing a new line

    """
    #: a user-friendly name for the algorithm
    name = Str('zeros algorithm')

    # list of names of traits defined in this class that the user needs
    # to set when the algorithm is applied
    arglist = []

    # instructions for user (description of algorithm and required args def)
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

    # instructions for user (description of algorithm and required args def)
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

    # instructions for user (description of algorithm and required args def)
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
