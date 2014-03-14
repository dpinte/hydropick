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
from traits.api import (Instance, HasTraits, Property, List,
                        Str, Dict, DelegatesTo, Event, on_trait_change)

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

    # dict stores info about each core sample for use by view
    core_info_dict = Dict

    #: depth_line instances representing bottom surface of lake = current surf
    lake_depths = DelegatesTo('survey_line')
    lake_depth_choices = List
    #: final choice for line used as current lake depth for volume calculations
    final_lake_depth = DelegatesTo('survey_line')

    # and event fired when the lake depths are updated
    lake_depths_updated = Event

    #: depth_line instances for pre-impoundment surfaces: below sediment
    preimpoundment_depths = DelegatesTo('survey_line', 'preimpoundment_depths')
    preimpoundment_depth_choices = List
    #: name of final choice for pre-impoundment depth to track sedimentation
    final_preimpoundment_depth = DelegatesTo('survey_line')

    # and event fired when the lake depth is updated
    preimpoundment_depths_updated = Event

    depth_lines_updated = Event

    # two values used to map image vertical pixel to actual depth.
    pixel_depth_offset = DelegatesTo('survey_line', 'draft')
    pixel_depth_scale = DelegatesTo('survey_line', 'pixel_resolution')

    # status of line determined by user analysis
    status = DelegatesTo('survey_line')

    # user comment on status (who approved it or why its bad fore example)
    status_string = DelegatesTo('survey_line')

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

    # xbounds used for each image display (arguably could be in view class)
    # Dict(freq_key_str, Tuple(min,max))
    xbounds = Property(Dict)

    # Y bounds should be set based on depth per pixel value of image data.
    # Y axis of depth lines should be set to match this value.
    ybounds = Property(Dict)

    # dict of depth value arrays for each freq/intensity plot to plot slices.
    y_arrays = Property(Dict)

    # cumulative distance along path based on locations array.
    cumulative_distance = Property()

    # dictionary of algorithms filled by the pane when new survey line selected
    algorithms = Dict

    ref_depth_line_name = Str('')

    #==========================================================================
    # Defaults
    #==========================================================================

    def _survey_line_default(self):
        s = SurveyLine()
        s.frequencies = {}
        return s

    def _core_info_dict_default(self):
        ''' make dictionary to store info for each core for ready access by
        view.  index can be used to dynamically change the absolute depth
        of boundaries plotted by indexing relevant depth line.
        '''
        cdict = {}
        for core in self.core_samples:
            i, p, d = self.get_nearest_point_to_core(core)
            pos_index, position, distance_from_line = i, p, d
            cdict[core.core_id] = (pos_index, position, distance_from_line)
        return cdict

    #==========================================================================
    # Notifications
    #==========================================================================

    @on_trait_change('target_choices')
    def update_depth_choices(self):
        ''' if target choices change it means a depth line is added or deleted
        so we need to update the lake depth and preimpoundmend depth choices'''
        if isinstance(self.lake_depths, dict):
            self.lake_depth_choices = self.lake_depths.keys()
        else:
            self.lake_depth_choices = []
        if isinstance(self.preimpoundment_depths, dict):
            self.preimpoundment_depth_choices = self.preimpoundment_depths.keys()
        else:
            self.preimpoundment_depth_choices = []

    #==========================================================================
    # Helper functions
    #==========================================================================

    def initialize_mask_xy(self):
        ''' called if no mask exists to set an initial mask at all False/0'''
        x = self.distance_array
        y = x * 0
        self.survey_line.mask = np.array((1 - y) == 0)
        logger.debug('initialized mask x_size, y_size = {},{}'
                     .format(x.size, y.size))

    def get_mask_xy(self):
        ''' get x, y arrays to plot from mask '''
        if self.survey_line.masked:
            x = self.distance_array
            ymax = self.ybounds[self.freq_choices[-1]][1]
            ys = np.ones_like(x) * ymax
            y = np.where(self.survey_line.mask, ys, ys * 0)
        else:
            x = np.array([])
            y = np.array([])
        return x, y

    def array_to_mask(self, array):
        ''' takes an array and converts it to boolean where nonzero = True
        then set this value in surveyline
        '''
        mask = np.array(array != 0)
        self.survey_line.mask = mask

    def get_nearest_point_to_core(self, core):
        ''' for given core find the closest point in the locations array
        to the core location and then use that index to get the
        associated distance along the survey line from the distance array.
        '''
        xy_pt = np.array(core.location)
        diff = self.locations - xy_pt
        dist_sq_array = np.sum(diff**2, axis=1)
        loc_index = np.argmin(dist_sq_array)
        core_location = self.distance_array[loc_index]
        distance_from_line = np.sqrt(dist_sq_array.min())
        return loc_index, core_location, distance_from_line

    def get_ref_depth_line(self):
        ''' works to get a valid lake depth line as a reference for core depths
        '''
        try:
            ref_line = self.lake_depths[self.ref_depth_line_name]
        except KeyError:
            try:
                ref_line = self.lake_depths[self.final_lake_depth]
            except KeyError:
                try:
                    self.ref_depth_line_name = 'current_surface_from_bin'
                    ref_line = self.lake_depths[self.ref_depth_line_name]
                except KeyError:
                    logger.error('cannot find a ref lake depth for core plot')
        return ref_line or None
    #==========================================================================
    # Get/Set
    #==========================================================================

    def _get_freq_choices(self):
        ''' Get list of available frequencies sorted lowest to highest
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
        for k, v in self.lake_depths.items():
            key = 'POST_' + k
            depth_dict[key] = v
        for k, v in self.preimpoundment_depths.items():
            key = 'PRE_' + k
            depth_dict[key] = v

        return depth_dict

    def _get_target_choices(self):
        ''' Get list of available lines to edit from depth_dict.
        also update the depth choices for final lines
        '''
        self.update_depth_choices()
        return self.depth_dict.keys()

    def _get_xbounds(self):
        ''' make dict of distance bounds for each frequency intensity array'''
        d = {}
        for key, trace_array in self.freq_trace_num.items():
            freq_dist = self.distance_array[trace_array - 1]
            d[key] = (freq_dist.min(), freq_dist.max())
        return d

    def _get_y_arrays(self):
        ''' y arrays for each freq provided in dictionary'''
        d = {}
        for key, intensity in self.frequencies.items():
            N = intensity.shape[0]
            min, max = self.ybounds[key]
            array = np.linspace(min, max, num=N)
            d[key] = array
        return d

    def _get_ybounds(self):
        ''' made dict of y bounds for each intensity plot'''
        d = {}
        min = np.mean(self.pixel_depth_offset)
        for key, intensity in self.frequencies.items():
            N = intensity.shape[0]
            max = min + N * self.pixel_depth_scale
            d[key] = (min, max)
        return d

    def _get_distance_array(self):
        ''' creates linear mapping of cumulative distance to trace_num array
        so each trace_num/index will have an approximate distance along line.
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
