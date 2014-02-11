#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

# std library
from copy import deepcopy
import logging
# other imports
import numpy as np

# ETS imports
from traits.api import (Instance, HasTraits, Array, Property, Float, List,
                        Str, Tuple, Dict, DelegatesTo, Event)

# Local imports
from ..model.survey_line import SurveyLine

logger = logging.getLogger(__name__)


class SurveyDataSession(HasTraits):
    """ Model for SurveyLineView.

    Assumes receipt of valid SurveyLine instance, and will remain bound
    to that instance until editing session is finished
    (Make sure surveyline has the traits delegated below from sdi dict )
    """

    # Source of survey line data to be edited
    survey_line = Instance(SurveyLine)

    ##### ITEMS COMING FROM SURVEY LINE #######################################

    #: sample locations, an Nx2 array (typically easting/northing?)
    locations = DelegatesTo('survey_line', 'locations')

    # lat/long for each pixel in line data arrays
    lat_long = DelegatesTo('survey_line', 'lat_long')

    #: a dictionary mapping frequencies to intensity arrays
    # NOTE:  assume arrays are transposed so that img_plot(array)
    # displays them correctly and array.shape gives (xsize,ysize)
    frequencies = Property(Dict)

    # dict of array of trace numbers for each freq => pixel location
    #: ! NOTE ! starts at 1, not 0, so need to subtract 1 to use as index
    freq_trace_num = DelegatesTo('survey_line', 'freq_trace_num')

    #: relevant core samples
    core_samples = DelegatesTo('survey_line', 'core_samples')

    #: depth_line instances representing bottom surface of lake = current surf
    lake_depths = DelegatesTo('survey_line')

    # and event fired when the lake depths are updated
    lake_depths_updated = Event

    #: depth_line instances for pre-impoundment surfaces: below sediment
    preimpoundment_depths = DelegatesTo('survey_line', 'preimpoundment_depths')

    # and event fired when the lake depth is updated
    preimpoundment_depths_updated = Event

    # two values used to map image vertical pixel to actual depth.
    pixel_depth_offset = DelegatesTo('survey_line', 'draft')
    pixel_depth_scale = DelegatesTo('survey_line', 'pixel_resolution')

    ##### ADDITIONAL TRAITS FOR FUNCTIONALITY #################################

    #: Dictionary of all depth lines. Allows editor easy access to all lines.
    depth_dict = Property(Dict)

    # array of approximate distance values for each index in trace_num
    distance_array = Property(depends_on=['survey_line.trace_num',
                                          'cumulative_distance'])

    # Keys of depth_dict provides list of target choices for line editor
    target_choices = Property(depends_on='depth_dict')

    # Selected target line key from depth dict for editing
    selected_target = Str

    # Sorted keys of frequencies dictionary.
    freq_choices = Property(List)

    # Selected freq key from frequencies dict for displaying image.
    # ------------ may be depricated -----------------------------------------
    #selected_freq = Str

    # Array to be used for x axis.  Length corresponds to depth lines and
    # image horizontal sizes.  Default is index but may be changed to
    # various actual distances.  Defines xbounds.
    #x_array = Property(Array)

    # xbounds used for each image display (arguably could be in view class)
    # Dict(freq_key_str, Tuple(min,max))
    xbounds = Property(Dict)

    # Y bounds should be set based on depth per pixel value of image data.
    # Y axis of depth lines should be set to match this value.
    ybounds = Property(Dict)

    # cumulative distance along path based on locations array.
    cumulative_distance = Property()


    #==========================================================================
    # Defaults
    #==========================================================================

    def _survey_line_default(self):
        s = SurveyLine()
        s.frequencies = {}
        return s

    # def _selected_freq_default(self):
    #     ''' start with lowest freq so we can change to hightest'''
    #     minf, maxf = self.get_low_high_freq()
    #     return minf

    #==========================================================================
    # Notifications
    #==========================================================================

    #==========================================================================
    # Helper functions
    #==========================================================================
    def get_x_array(self, index_array):
        ''' Get x values in approx distance for arbitrary index value set'''
        xarray = self.distance_array[index_array]
        return xarray

    #==========================================================================
    # Get/Set
    #==========================================================================
    # def get_low_high_freq(self):
    #     ''' gets lowest/highest freq'''
    #     freqs = self.frequencies.keys()
    #     fsorted = sorted(freqs, key=lambda freqs: float(freqs))
    #     minf, maxf = fsorted[0], fsorted[-1]
    #     return minf, maxf

    def _get_freq_choices(self):
        ''' Get list of available frequencies as (value,string) pair from
        frequencies dict for use in selector widget.
        Limit label string resolution to 0.1 kHz.
        '''
        try:
            keys = self.frequencies.keys()
            s = sorted(keys, key=lambda f: float(f))
        except ValueError:
            s = sorted(self.frequencies.keys())
            logging.error('cannot convert freq key to float. using str sort')
        return s

    def _get_frequencies(self):
        new_dict = deepcopy(self.survey_line.frequencies)
        return new_dict

    def _get_depth_dict(self):
        ''' Combine lake depths and preimpoundment in to one dict.
        '''
        depth_dict = {}
        depth_dict.update(self.lake_depths)
        depth_dict.update(self.preimpoundment_depths)
        return depth_dict

    def _get_target_choices(self):
        ''' Get list of available frequencies as strings from frequencies dic
        limit resolution to 0.1 kHz.
        '''
        return self.depth_dict.keys()

    def _get_xbounds(self):
        ''' make dict of distance bounds for each frequency intensity array'''
        d = {}
        for key, trace_array in self.freq_trace_num.items():
            freq_dist = self.distance_array[trace_array-1]
            d[key] = (freq_dist.min(), freq_dist.max())
        return d

    def _get_ybounds(self):
        d={}
        min = np.mean(self.pixel_depth_offset)
        for key, intensity in self.frequencies.items():
            N = intensity.shape[0]
            max = min + N * self.pixel_depth_scale
            d[key] = (min, max)
        return d

    def _get_distance_array(self):
        ''' creates linear mapping of cumulative distance to the trace_num array
        so each trace_num/index will have an approximate distance along the line.
        This can be used to get an x_value array for any function defined on a
        subset of the trace_num array via x_array = distance[index_array]
        '''
        max = self.cumulative_distance[-1]
        N = float(self.cumulative_distance.size)
        linear_dist = (self.survey_line.trace_num - 1) * max / (N - 1)
        return linear_dist

    def _get_cumulative_distance(self):
        ''' discretely sum up distance along location points.

        Locations array given as pts=[(x,y)...].
        ds = dx**2 + dy**2 ,  do this in parallel on the arrays:
        assume shape is (N,2)

        Returns (N,1) array of cumulative distance pts.

        Could also return (N-1,1) array of ds points =
                              distance between each pt.
        '''
        # diff array is last N-1 pts - first N-1 pts
        pts = self.locations
        diff_array = pts[1:] - pts[:-1]
        # now get sqr(dx**2 + dy**2)
        ds = np.sqrt(np.sum(diff_array**2, axis=1))
        s = np.concatenate(([0], np.cumsum(ds)))
        return s

if __name__ == '__main__':
    pass
