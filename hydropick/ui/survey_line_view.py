#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import numpy as np

# ETS imports
from traits.api import (Instance, Str, Dict, List, Int, Property,
                        on_trait_change)
from traitsui.api import ModelView, View, VGroup
from chaco.api import Plot, ArrayPlotData, PlotComponent, Greys

# Local imports
from ..model.depth_line import DepthLine
from .survey_data_session import SurveyDataSession
from .survey_tools import TraceTool, LocationTool
from .survey_views import (ControlView, InstanceUItem, PlotContainer, DataView,
                           ImageAdjustView, AddDepthLineView)


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

    # Defines view for pop up image adjustments window
    image_adjust_view = Instance(ImageAdjustView)

    # defines popup window for new depth line creation
    add_depth_line_view = Instance(AddDepthLineView)

    # Dictionary of plots kept for legend and for tools.
    # Will contain all depth lines at least.  This contains components as
    # opposed to the depth_dict{str:array} in the model.
    plot_dict = Dict(Str, PlotComponent, value={})

    # Custom tool for editing depth lines
    trace_tool = Instance(TraceTool)

    # Custom tool for showing coordinates at mouse position
    location_tool = Instance(LocationTool)

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
        ''' Creat initial plot container'''
        dist_unit = self.model.survey_line.locations_unit
        self.mainplot = self.make_plot()
        self.mainplot.y_axis.title = 'Depth (m)'
        self.miniplot = self.make_plot(height=self.mini_height)
        self.miniplot.x_axis.title = 'Distance ({})'.format(dist_unit)
        container = PlotContainer(mainplot=self.mainplot,
                                  miniplot=self.miniplot)
        if self.model.depth_dict:
            self.add_lines(**self.model.depth_dict)
        if self.model.frequencies:
            self.add_images(**self.model.frequencies)

        container.on_trait_change(self.legend_capture,
                                  name='legend_highlighter._drag_state')

        # need to change selected freq to
        minf, maxf = self.model.get_low_high_freq()
        self.model.selected_freq = minf
        self.model.selected_freq = maxf
        return container

    def _control_view_default(self):
        ''' Creates ControlView object filled with associated traits'''

        cv = ControlView(target_choices=self.model.target_choices,
                         line_to_edit=self.model.selected_target,
                         visible_lines=[],
                         freq_choices=self.model.freq_choices,
                         image_freq=self.model.selected_freq,
                         latitude=0,
                         longitude=0
                         )
        # set default values for widgets
        cv.visible_lines = self.model.target_choices
        cv.image_freq = self.model.selected_freq

        # Add notifications
        cv.on_trait_change(self.select_line, name='visible_lines')
        cv.on_trait_change(self.change_target, name='line_to_edit')
        cv.on_trait_change(self.change_image, name='image_freq')
        cv.on_trait_change(self.toggle_edit, name='edit')

        # need to change selected freq to
        minf, maxf = self.model.get_low_high_freq()
        self.model.selected_freq = minf
        self.model.selected_freq = maxf
        return cv

    def _add_depth_line_view_default(self):
        return AddDepthLineView(depth_line=DepthLine())

    def toggle_edit(self):
        ''' enables editing tool based on ui edit selector'''
        if self.control_view.edit == 'Editing':
            self.trace_tool.edit_allowed = True
        else:
            self.trace_tool.edit_allowed = False

    def _plotdata_default(self):
        ''' Provides initial plotdata object'''
        if self.model.x_array.any():
            return ArrayPlotData(x_array=self.model.x_array)
        else:
            return ArrayPlotData()

    def _trace_tool_default(self):
        ''' Sets up trace tool for editing lines'''
        tool = TraceTool(self.mainplot)
        tool.on_trait_change(self.update_depth, 'depth')
        self.mainplot.tools.append(tool)
        return tool

    def _data_view_default(self):
        return DataView()

    def _image_adjust_view_default(self):
        imv = ImageAdjustView()
        imv.on_trait_change(self.adjust_image, name='contrast_brightness')
        imv.on_trait_event(self.adjust_image, name='invert')
        return imv

    #==========================================================================
    # Helper functions
    #==========================================================================
    def update_control_view(self):
        cv = self.control_view
        cv.visible_lines = self.model.target_choices
        cv.target_choices = self.model.target_choices

    def add_lines(self, **kw):
        ''' Take arbitrary number of key=array pairs.
        Adds them to
        self.plotdata then self.depth_dict,
        adds them to mainplot and miniplot,
        adds the comonents to self.plot_dict'''

        line_dict = dict([(k, v.depth_array) for k, v in kw.items()])
        self.plotdata.update_data(line_dict)
        #        self.model.preimpoundment_depths.update(kw)
        self.update_main_mini_lines(kw.keys())
        self.update_control_view()

    def add_images(self, **kw):
        ''' Adds images same way as lines to plotdata and plots first one
        '''
        self.plotdata.update_data(kw)
        self.model.frequencies.update(kw)
        imagelist = [kw.keys()[0]]
        self.update_main_mini_image(imagelist)

    def make_plot(self, height=None):
        ''' Creates one Plot instance with all depthlines and one image plot.
        Used for mainplot and miniplot to make identical plots apart from
        height.
        '''
        plot = Plot(self.plotdata,
                    border_visible=True,
                    bgcolor="white",
                    padding=0,
                    origin='top left'
                    )
        if height:
            plot.height = height
            plot.resizable = 'h'

        return plot

    def update_main_mini_lines(self, keylist=[]):
        ''' Add specified lineplots already in self.plotdata to both plots
        Assumes x_array from model.x_array is already in plotdata as well.
        '''
        main = self.mainplot
        mini = self.miniplot
        for key in keylist:
            newplot = main.plot(('x_array', key), color='blue', name=key)
            self.plot_dict[key] = newplot[0]
            mini.plot(('x_array', key), color='blue', name=key)
        self.mainplot.invalidate_and_redraw()

    def update_main_mini_image(self, keylist=[], remove=None):
        ''' Add specified image plots from self.plotdata to both plots.
        Should be done after lineplots to set plot axis ranges automatically
        '''
        main = self.mainplot
        mini = self.miniplot
        for key in keylist:
            newplot = main.img_plot(key, colormap=Greys,
                                    xbounds=self.model.xbounds,
                                    ybounds=self.model.ybounds,
                                    name=key)
            self.trace_tool.image = newplot[0]
            self.location_tool = LocationTool(newplot[0])
            self.location_tool.on_trait_change(self.update_locations,
                                               'image_index')
            newplot[0].tools.append(self.location_tool)

            self.plot_dict[key] = newplot[0]
            mini.img_plot(key, colormap=Greys,
                          xbounds=self.model.xbounds,
                          ybounds=self.model.ybounds,
                          name=key)
        if remove:
            mini.plots.pop(remove)[0]
            main.plots.pop(remove)[0]

        self.mainplot.invalidate_and_redraw()

    #==========================================================================
    # Get/Set methods
    #==========================================================================

    def _get_algorithm_list(self):
        ''' provides list of choice for available algorithms to UI'''
        return tuple(self.algorithms.keys())
    #==========================================================================
    # Notifications or Callbacks
    #==========================================================================

    def legend_capture(self,obj, name, old, new):
        ''' stop editing depth line when moving legend (rt mouse button)'''
        self.control_view.edit = 'Not Editing'

    def image_adjustment_dialog(self):
        self.image_adjust_view.configure_traits()

    def show_data_dialog(self):
        self.data_view.configure_traits()

    def new_algorithm_line_dialog(self):
        ''' called from UI button to bring up add line dialog'''
        self.add_depth_line_view.configure_traits()

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
        dv.latitude = lat
        dv.longitude = long
        dv.easting = east
        dv.northing = north

    def adjust_image(self, obj, name, old, new):
        ''' Given a tuple (contrast, brightness) with values
        from 0 to 10, -1 to 1'''
        data = self.model.frequencies[self.model.selected_freq]
        if name == 'invert':
            data = 1-data
        elif name == 'contrast_brightness':
            c, b = new
            data = c * data
            b2 = c * b - b
            b3 = b2 + 1
            data = np.clip(data, b2, b3)
            if getattr(obj, 'invert'):
                data = 1-data
        self.plotdata.set_data(self.model.selected_freq,
                               data)

    def update_depth(self, depth):
        ''' Called by trace tool to update depth readout display'''
        self.data_view.depth = depth

    def change_target(self, object, name, old, new_target):
        '''update trace tool target line attribute.'''
        new_target_line = self.plot_dict[new_target]
        new_target_line.color = 'red'
        old_target_line = self.plot_dict.get(old, None)
        if old_target_line:
            old_target_line.color = 'blue'
        # make selected plot visible
        cv = self.control_view
        if new_target not in cv.visible_lines:
            newset = set(cv.visible_lines).union(set([new_target]))
            cv.visible_lines = list(newset)
        self.mainplot.invalidate_and_redraw()
        self.trace_tool.target_line = new_target_line

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
