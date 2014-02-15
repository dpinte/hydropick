#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import logging
import numpy as np

# ETS imports
from traits.api import (Instance, Str, Dict, List, Int, Property,
                        on_trait_change)
from traitsui.api import ModelView, View, VGroup

from chaco.api import (Plot, ArrayPlotData, PlotComponent)

# Local imports
from ..model.depth_line import DepthLine
from .survey_data_session import SurveyDataSession
from .survey_tools import TraceTool, LocationTool, DepthTool
from .survey_views import (ControlView, InstanceUItem, PlotContainer, DataView,
                           ImageAdjustView, AddDepthLineView,
                           HPlotSelectionView)
from ..model.core_sample import CoreSample

logger = logging.getLogger(__name__)
EDIT_COLOR = 'black'


class SurveyLineView(ModelView):
    """ View Class for working with survey line data to find depth profile.

    Uses a Survey class as a model and allows for viewing of various depth
    picking algorithms and manual editing of depth profiles.
    """

    #==========================================================================
    # Traits Attributes
    #==========================================================================

    # Data model is SurveyDataSession class which starts with SurveyLine object
    # containing core data, SDI survey data, lake data.
    model = Instance(SurveyDataSession)

    # Defines view for all the plots.  Place beside control view
    plot_container = Instance(PlotContainer)

    # Defines view for all the plot controls and info. Sits by plot container.
    control_view = Instance(ControlView)

    # Defines view for pop up location data window
    data_view = Instance(DataView)

    # Defines view for pop up location data window
    plot_selection_view = Instance(HPlotSelectionView)

    # Defines view for pop up image adjustments window
    image_adjust_view = Instance(ImageAdjustView)

    # defines popup window for new depth line creation
    add_depth_line_view = Instance(AddDepthLineView)

    # Dictionary of plots kept for legend and for tools.
    # Will contain all depth lines at least.  This contains components as
    # opposed to the depth_dict{str:array} in the model.
    plot_dict = Dict(Str, PlotComponent)

    # Custom tool for editing depth lines
    trace_tools = Dict

    # Custom tool for showing coordinates and other info at mouse position
    location_tools = Dict

    # Custom tool for showing depth values at mouse position
    depth_tools = Dict

    # List of which lines are visible in plots
    visible_lines = List([])

    # plotdata is the ArrayPlotData instance holding the plot data.
    # for now it contains available images and multiple line plots for depths.
    plotdata = Instance(ArrayPlotData)

    # dict to remember image control (b&c) settings for each freq
    image_settings = Dict

    # Pair of combined plots:  main for editing; mini for scanning
    mainplot = Instance(Plot)
    miniplot = Instance(Plot)
    mini_height = Int(100)

    # traits for adding new lines based on algoriths
    # dictionary of available algoritms
    algorithms = Dict
    algorithm_list = Property(depends_on='algorithms')

    # name chosen from UI to apply
    algorithm_name = Str

    # name to give to resulting depth line
    new_line_name = Str
    #==========================================================================
    # Define Views
    #==========================================================================

    traits_view = View(
        VGroup(
            InstanceUItem('control_view'),
            InstanceUItem('plot_container'),
        ),
        resizable=True,
    )

    #==========================================================================
    # Defaults
    #==========================================================================

    def _plot_container_default(self):
        ''' Create initial plot container'''
        container = PlotContainer()
        return container

    @on_trait_change('model')
    def update_plot_container(self):
        self.create_data_array()
        c = self.plot_container
        c.plot_dict = self.plot_dict
        c.data = self.plotdata
        c.model = self.model
        logger.info('cores={}'.format(self.model.core_samples))
        # need to call tools to activate defaults
        start_tools = self.location_tools
        start_tools = self.depth_tools
        c.vplot_container.invalidate_and_redraw()

    def _control_view_default(self):
        ''' Creates ControlView object filled with associated traits'''

        cv = ControlView(target_choices=self.model.target_choices,
                         line_to_edit=self.model.selected_target,
                         freq_choices=self.model.freq_choices,
                         image_freq='',
                         )
        # set default values for widgets
        cv.image_freq = ''

        # Add notifications
        cv.on_trait_change(self.change_target, name='line_to_edit')
        cv.on_trait_change(self.change_image, name='image_freq')
        cv.on_trait_change(self.toggle_edit, name='edit')

        return cv

    def _add_depth_line_view_default(self):
        if len(self.model.core_samples) > 0:
            core = self.model.core_samples[0]
        else:
            core = CoreSample()
        if self.model.depth_dict:
            dline = self.model.depth_dict.values()[0]
        else:
            dline = DepthLine()
        return AddDepthLineView(depth_line=dline,
                                core=core,
                                corelist=self.model.core_samples
                                )

    def _plot_selection_view_default(self):
        freq_choices = self.model.freq_choices
        return HPlotSelectionView(hplot_choices=freq_choices,
                                  visible_frequencies=freq_choices,
                                  intensity_profile=True
                                  )

    def toggle_edit(self):
        ''' enables editing tool based on ui edit selector'''
        for tool in self.trace_tools.values():
            if self.control_view.edit == 'Editing':
                tool.edit_allowed = True
            else:
                tool.edit_allowed = False

    def _plotdata_default(self):
        ''' Provides initial plotdata object'''
        return ArrayPlotData()

    def _trace_tools_default(self):
        ''' Sets up trace tool for editing lines'''
        tools = {}
        for key, hpc in self.plot_container.hplot_dict.items():
            if key is not 'mini':
                main = hpc.components[0]
                tool = TraceTool(main)
                main.tools.append(tool)
                tools[key] = tool
        return tools

    def _location_tools_default(self):
        ''' Sets up location tools for intensity images'''
        tools = {}
        for key, hpc in self.plot_container.hplot_dict.items():
            if key is not 'mini':
                main = hpc.components[0]
                img = main.plots[key][0]
                tool = LocationTool(img)
                tool.on_trait_change(self.update_locations, 'image_index')
                img.tools.append(tool)
                tools[key] = tool
        return tools

    def _depth_tools_default(self):
        ''' Sets up location tools for intensity images'''
        tools = {}
        for key, hpc in self.plot_container.hplot_dict.items():
            if key is not 'mini':
                main = hpc.components[0]
                tool = DepthTool(main)
                tool.on_trait_change(self.update_depth, 'depth')
                main.tools.append(tool)
                tools[key] = tool
        return tools

    def _data_view_default(self):
        return DataView()

    def _image_adjust_view_default(self):
        iav = ImageAdjustView()
        iav.freq_choices = self.model.freq_choices
        iav.on_trait_change(self.adjust_image, name='contrast_brightness')
        iav.on_trait_event(self.adjust_image, name='invert')
        iav.on_trait_event(self.adjust_image, name='frequency')
        return iav

    #==========================================================================
    # Helper functions
    #==========================================================================

    def create_data_array(self):
        '''want data array to have all data in it :
            3x img    min=1  (1 per hplot)
            3x img depth value array (1 per hplot, used for slice plotting)
            3x x_slice min=3 (1 per hplot)
            nx lines  min=0  (all on each hplot)

            data keys:
            intensity images key = freq
            img depth arrays key = freq_y
            slice line key = freq_slice
            depth line key = prefix_line_name_x

        '''

        if self.plotdata is None:
            self.plotdata = ArrayPlotData()
        d = self.plotdata

        if self.model:
            # add the freq dependent (3@) data
            for k, img in self.model.frequencies.items():
                y_key = k+'_y'
                slice_key = k+'_slice'
                kw = {k: self.model.frequencies[k],
                      y_key: self.model.y_arrays[k],
                      slice_key: np.array([]),
                      }
                d.update_data(**kw)

            # add the depth line data
            for line_key, depth_line in self.model.depth_dict.items():
                x = self.model.distance_array[depth_line.index_array]
                y = depth_line.depth_array
                key_x, key_y = line_key + '_x',  line_key + '_y'
                kw = {key_x: x, key_y: y}
                d.update_data(**kw)

        return d

    def update_control_view(self):
        cv = self.control_view
        cv.visible_lines = self.model.target_choices
        cv.target_choices = self.model.target_choices

    #==========================================================================
    # Get/Set methods
    #==========================================================================

    def _get_algorithm_list(self):
        ''' provides list of choice for available algorithms to UI'''
        return tuple(self.algorithms.keys())
    #==========================================================================
    # Notifications or Callbacks
    #==========================================================================

    def legend_capture(self, obj, name, old, new):
        ''' stop editing depth line when moving legend (rt mouse button)'''
        self.control_view.edit = 'Not Editing'

    def image_adjustment_dialog(self):
        self.image_adjust_view.configure_traits()

    def show_data_dialog(self):
        self.data_view.configure_traits()

    def new_algorithm_line_dialog(self):
        ''' called from UI button to bring up add line dialog'''
        self.add_depth_line_view.configure_traits()

    def plot_view_selection_dialog(self):
        ''' called from view menu to edit which plots to view'''
        self.plot_selection_view.configure_traits()

    @on_trait_change('plot_selection_view.visible_frequencies')
    def change_visible_frequencies(self):
        ''' update visible hplots based on visible freq checkboxes'''
        vis_hplots = self.plot_selection_view.visible_frequencies
        self.plot_container.selected_hplots = vis_hplots
        self.plot_container.set_hplot_visibility()

    @on_trait_change('plot_selection_view.intensity_profile')
    def change_intensity_profile_visibility(self):
        ''' update visible hplots based on visible freq checkboxes'''
        show_profile = self.plot_selection_view.intensity_profile
        self.plot_container.show_intensity_profiles = show_profile
        self.plot_container.set_intensity_profile_visibility(show_profile)

    @on_trait_change('apply_button')
    def add_algorithm_line(self):
        ''' result of applying selected algorithm.  Makes new depth line'''
        algorithm = self.algorithms[self.algorithm_name]()     # add args?
        new_line_data = algorithm.process_line(self.model.survey_line)
        new_line_dict = {str(self.new_line_name): new_line_data}
        self.add_lines(**new_line_dict)

    def update_locations(self, image_index):
        ''' Called by location_tool to update display readouts as mouse moves
        '''
        dv = self.data_view
        lat, long = self.model.lat_long[image_index]
        east, north = self.model.locations[image_index]
        power = self.model.survey_line.power[image_index]
        gain = self.model.survey_line.gain[image_index]
        dv.latitude = lat
        dv.longitude = long
        dv.easting = east
        dv.northing = north
        dv.power = power
        dv.gain = gain

    def adjust_image(self, obj, name, old, new):
        ''' Given a tuple (contrast, brightness) with values
        from 0 to CONTRAST_MAX, 0 to 1
        if frequency is changed, update view which will update plots.
        if other values are changed and there is a freq, it will
        update data with new values and save settings'''
        iav = self.image_adjust_view
        if name is 'frequency':
            # changed freq : update settings
            freq = new
            c, b, i = self.image_settings.setdefault(freq, [1, 0, True])
            iav.contrast, iav.brightness, iav.invert = c, b, i
        else:
            if iav.frequency:
                freq = iav.frequency
                if name == 'invert':
                    self.image_settings[freq][2] = new
                    self.apply_image_settings(freq)
                elif name == 'contrast_brightness':
                    self.image_settings[freq][:2] = new
                self.apply_image_settings(freq)

    def apply_image_settings(self, freq):
        ''' apply saved image settings to this freq (or set default).
        always reapply changes from original data.
        apply to plot data'''
        c, b, invert = self.image_settings.setdefault(freq, [1, 0, True])
        data = self.model.frequencies[freq]
        data = c * data
        b2 = c * b - b
        b3 = b2 + 1
        data = np.clip(data, b2, b3)
        if invert:
            data = 1-data
        self.plot_container.data.update_data({freq: data})

    def update_depth(self, depth):
        ''' Called by trace tool to update depth readout display'''
        self.data_view.depth = depth

    def change_target(self, object, name, old, new_target):
        '''update trace tool target line attribute.'''
        self.plot_dict = self.plot_container.plot_dict
        # change colors of lines appropriately
        for key in self.model.freq_choices:
            new_plot_key = key + '_' + new_target
            new_target_line = self.plot_dict[new_plot_key]
            new_target_line.color = EDIT_COLOR
            old_plot_key = key + '_' + old
            old_target_line = self.plot_dict.get(old_plot_key, None)
            if old_target_line:
                old_color = self.model.depth_dict[new_target].color
                old_target_line.color = old_color
            # update trace_tool targets.
            tool = self.trace_tools[key]
            tool.target_line = new_target_line
            tool.key = new_target
        self.plot_container.vplot_container.invalidate_and_redraw()

    def change_image(self, old, new):
        ''' Called by changing selected freq.
        Loads new image and recalls saved B&C '''
        iav = self.image_adjust_view
        if old:
            self.image_settings[old] = [iav.contrast,
                                        iav.brightness,
                                        iav.invert]
        self.model.selected_freq = new
        c, b, i = self.image_settings.get(new, [1, 0, True])
        iav.contrast, iav.brightness, iav.invert = c, b, i
        if old in self.plot_dict:
            self.update_main_mini_image([new], remove=old)
        else:
            self.update_main_mini_image([new])

    def select_line(self, object, name, old, visible_lines):
        ''' Called when controlview.visible_lines changes in order to actually
        change the visibility of the lines.  Need to make sure the new list
        includes the selected lines which means if someone unchecks it we have
        to not only make it visible but add it to visible lines which will
        re-call this method'''

        newset = set(visible_lines)
        cv = self.control_view

        if cv.line_to_edit:
            # If there is line to edit, make sure its in visible lines list.
            # Temporarily disable notification so we don't re-call this method.
            fullset = newset.union(set([cv.line_to_edit]))
            cv.on_trait_change(self.select_line, name='visible_lines',
                               remove=True)
            cv.visible_lines = list(fullset)
            cv.on_trait_change(self.select_line, name='visible_lines')

        else:
            fullset = newset

        # now set correct visibilties
        for name in self.model.depth_dict:
            this_plot = self.mainplot.plots[name][0]
            if name in fullset:
                this_plot.visible = True
            else:
                this_plot.visible = False
        self.mainplot.invalidate_and_redraw()
