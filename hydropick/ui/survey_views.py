#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

""" View definitions for controlling layout of survey line editor task

Views are:
*BigView:
    Example of use for  overall layout with Controls on left and Plots on
    right.
*PlotView:
    Sets plot view which may be just the plot component and legend.
*ControlView:
    Set layout of controls and information displays
"""
# Std lib imports

# other imports
import numpy as np

# ETS imports
from enable.api import ComponentEditor
from traits.api import (Instance, Str, List, HasTraits, Float, Property,
                        Button, Enum, Bool)
from traitsui.api import (View, Group, Item, EnumEditor, UItem, InstanceEditor,
                          RangeEditor, Label, HGroup)
from chaco.api import (Plot, ArrayPlotData, LinePlot, VPlotContainer,
                       CMapImagePlot, ScatterPlot, ColorBar, LinearMapper,
                       HPlotContainer, Legend)
from chaco.tools.api import (PanTool, ZoomTool, RangeSelection,
                             RangeSelectionOverlay, LegendHighlighter)

# Local imports
from ..model.depth_line import DepthLine
from .survey_tools import InspectorFreezeTool


class InstanceUItem(UItem):
    '''Convenience class for inluding instance in view as Item'''

    style = Str('custom')
    editor = Instance(InstanceEditor, ())


class PlotContainer2(HasTraits):
    ''' miniplot must have at least one plot with an index.
        therefore there should be a check in the plot dictionary
        that there is a plot with an index
    '''

    #==========================================================================
    # Traits Attributes
    #==========================================================================

    # Vplotcontainer will have mmainplot on top for working and small miniplot
    # below for reference
    plot_container = Instance(VPlotContainer)

    model = Instance(DataModel)
    data = Instance(ArrayPlotData)

    hplot_dict = Dict
    selected_hplots = List
    legend_dict = Dict
    inspector_freeze_tool = Instance(InspectorFreezeTool)

    mini_height = Int(150)
    slice_plot_width = Int(100)
    hplot_padding = Int(5)
    main_padding = Int(15)
    #==========================================================================
    # Define Views
    #==========================================================================

    traits_view = View(UItem('vplotcontainer',
                             editor=ComponentEditor(),
                             show_label=False),
                        )

    #==========================================================================
    # Defaults
    #==========================================================================
    def _vplotcontainer_default(self):
        self.create_empty_plot()

    def _inspector_freeze_tool_default(self):
        tool = InspectorFreezeTool(tool_set=set())
        return tool

    #==========================================================================
    # Helper functions
    #==========================================================================
    def create_empty_plot(self):
        ''' place filler
        '''
        vpc = VPlotContainer(bgcolor='lightgrey', height=1000, width=800)
        self.vplotcontainer = vpc
        return vpc

    def create_vplot(self):
        ''' fill vplot container with 1 mini plot for range selection
        and N main plots ordered from to top to bottom by freq
        '''
        vpc = VPlotContainer(bgcolor='lightgrey')
        if self.model.freq_choices:
            # create mini plot using the highest freq as background
            keys = self.model.freq_choices
            mini = self.create_hplot(key=keys[-1], mini=True)
            self.mini_hplot = mini
            vpc.add(mini)

            # create hplot containers for each freq and add to dict.
            # dictionary will be used to access these later to individually
            # address them to turn them on or off etc.
            # note these are added with lowest freq on bottom
            for freq in self.model.freq_choices:
                hpc = self.create_hplot(key=freq)
                self.hplot_dict[freq] = hpc
                vpc.add(hpc)

        # add tool to freeze line inspector cursor when in desired position
        vpc.tools.append(self.inspector_freeze_tool)

        self.vplot_container = vpc
        self.set_hplot_visibility()

    def set_hplot_visibility(self):
        ''' to be called when selected hplots are changed
        For selected hplots set the hplot, legend, and axis visibility'''
        sorted_hplots = [f for f in self.model.freq_choices
                         if f in self.selected_hplots]

        if sorted_hplots:
            bottom = sorted_hplots[0]
            top = sorted_hplots[-1]

        for freq, hpc in self.hplot_dict.items():
            hpc.visible = (freq in sorted_hplots)
            hpc.components[0].x_axis.visible = (freq == bottom)
            legend = self.legend_dict[freq]
            legend.visible = (freq == top)

    def create_hplot(self, key=None, mini=False):
        if mini:
            hpc = HPlotContainer(bgcolor='darkgrey',
                                 height=self.mini_height,
                                 resizable='h',
                                 padding=self.hplot_padding
                                 )
        else:
            hpc = HPlotContainer(bgcolor='lightgrey',
                            padding = self.hplot_padding
                            )

        # make slice plot for showing intesity profile of main plot
        slice_plot = Plot(self.data,
                          width=self.slice_plot_width,
                          orientation="v",
                          resizable="v",
                          padding=self.main_padding,
                          bgcolor='beige'
                          )

        slice_plot.x_axis.visible = False
        slice_key = key + '_slice'
        ydata_key = key + 'y'
        slice_plot.plot((key+'y', slice_key))

        # make main plot for editing depth lines
        main = Plot(self.data,
                    border_visible=True,
                    bgcolor='beige'
                    origin='top left',
                    padding=self.main_padding
                    )

        # add intensity img to plot
        img_plot = main.img_plot(key, name=key,
                                 xbounds=self.model.x_bounds[key],
                                 ybounds=self.model.y_bounds[key]
                                 )
        # add line plots: use method since these may change
        self.update_line_plots(plot)

        # now add tools depending if it is a mini plot or not
        if mini:
            # add range selection tool only
            # first add a reference line to attache it to
            reference = self.make_reference_plot()
            main.add(reference)
            # attache range selector to this plot
            range_tool = RangeSelection(reference)
            reference.tools.append(range_tool)
            range_overlay = RangeSelectionOverlay(reference,
                                                  metadata_name="selections")
            refplot.overlays.append(range_overlay)
            range_tool.on_trait_change(self._range_selection_handler,
                                       "selection")
            # add to hplot and dict
            hpc.add(main)
            self.hplot_dict['mini'] = hpc

        else:
            # add zoom tools
            main.tools.append(PanTool(main))
            main.tools.append(ZoomTool(main, tool_mode='range', axis='value'))

            # add line inspector and attach to freeze tool
            line_inspector = LineInspector(component=img_plot,
                                               axis='index_x',
                                               inspect_mode="indexed",
                                               is_interactive=True,
                                               write_metadata=True,
                                               metadata_name='x_slice',
                                               is_listener=True,
                                               color="white")
            img_plot.overlays.append(line_inspector)
            self.inspector_freeze_tool.tool_set.add(line_inspector)

            # add listener for changes to metadata made by line inspector
            img_plot.on_trait_change(self.metadata_changed, 'index.metadata')

            # add clickable legend ; must update legend when depth_dict updated
            legend = Legend(component=main, padding=0,
                            align="ur", font='modern 8')
            legend_highlighter = LegendHighlighter(legend,
                                                        drag_button="right")
            legend.tools.append(self.legend_highlighter)
            for k,v in self.model.depth_dict:
                legend.plots[k] = main.plots[k]
            legend.visible = False
            self.legend_dict[key] = legend
            main.overlays.append(legend)

            # add main and slice plot to hplot container and dict
            hpc.add(main,slice_plot)
            self.hplot_dict[key] = hpc

        return hpc

        # add 'reference' plot for range selector tool to cover entire range
    def update_line_plots(self, key, plot):
        ''' takes a Plot object and adds all available line plots to it.
        Each Plot.plots has one img plot labeled by freq key and the rest are
        line plots.  When depth_dict is updated, check all keys to see all
        lines are plotted'''

        for line_key, depth_line in self.model.depth_dict.items():
            not_plotted = line_key not in plot.plots
            not_image = line_key not in self.model.freq_choices
            if not_plotted and not_image:
                self.plot_depth_line(key, line_key, depth_line, plot)

    def plot_depth_line(self, key, line_key, depth_line, plot):
        ''' plot a depth_line using a depth line object'''

        # add data to ArrayPlotData if not there
        if line_key not in self.data.arrays.keys()
            x = self.model.distance_array[depth_line.index_array]
            y = depth_line.depth_array
            key_x, key_y = line_key + '_x',  line_key + '_y'
            self.data.update({key_x: x, key_y: y})

        # now plot
        line_plot = plot.plot((key_x, key_y),
                              color=depth_line.color,
                              name=line_key
                              )
        # match vertical to ybounds in case there are pathological points
        line_plot.value_range.low = plot.plots[key].ybounds[0]
        line_plot.value_range.high = plot.plots[key].ybounds[1]

    def make_reference_plot(self, plot)
        x_pts = np.array([self.model.distance_array.min(),
                          self.model.distance_array.max()]
                          )
        y_pts = 0 * x_pts
        ref_plot = create_scatter_plot((x_pts, y_pts), color = 'black')
        return ref_plot


    #==========================================================================
    # Notifiers and Handlers
    #==========================================================================
    def _range_selection_handler(self, event):
        # The event obj should be a tuple (low, high) in data space
        if event is not None:
            #adjust index range for main plots
            low, high = event
            for key,hpc in self.hplot_dict.items():
                if key is not 'mini':
                    this_plot = hpc.components[0]
                    this_plot.index_range.low = low
                    this_plot.index_range.high = high
        else:
            # reset range back to full/auto for main plots
            for key,hpc in self.hplot_dict.items():
                if key is not 'mini':
                    this_plot = hpc.components[0]
                    this_plot.index_range.set_bounds("auto", "auto")


class PlotContainer(HasTraits):
    ''' miniplot must have at least one plot with an index.
        therefore there should be a check in the plot dictionary
        that there is a plot with an index
    '''

    #==========================================================================
    # Traits Attributes
    #==========================================================================

    # These two plots should have the same data.  The miniplot will provide a
    # continuous full view of data set.
    mainplot = Instance(Plot)
    miniplot = Instance(Plot)
    # Vplotcontainer will have mmainplot on top for working and small miniplot
    # below for reference
    plot_container = Instance(VPlotContainer)

    # trait used to signal editor when legend is moved (rt drag) => stop edit.
    legend_highlighter = Instance(LegendHighlighter)

    # View for the plot container
    traits_view = View(UItem('plot_container', editor=ComponentEditor()))

    #==========================================================================
    # Defaults
    #==========================================================================

    def _mainplot_default(self):
        return self.default_plot()

    def _miniplot_default(self):
        return self.default_plot()

    def default_plot(self):
        # Provides initial line plot to satisfy range tool.  Subsequent plots
        # should have at least one line plot
        y = np.arange(10)
        data = ArrayPlotData(y=y)
        plot = Plot(data)
        plot.plot(('y'))
        return plot

    # Add a range overlay to the miniplot that is hooked up to the range
    # of the main plot.

    def _plot_container_default(self):
        ''' Define plot container tools and look.
        '''
        self.mainplot.tools.append(PanTool(self.mainplot))
        self.mainplot.tools.append(ZoomTool(self.mainplot,
                                            tool_mode='range',
                                            axis='value')
                                   )
        main = self.mainplot

        # Make clickable, dragable legend.
        legend = Legend(component=main, padding=10, align="ur")
        self.legend_highlighter = LegendHighlighter(legend,
                                                    drag_button="right")
        legend.tools.append(self.legend_highlighter)
        legend.plots = dict([(k, v) for k, v in main.plots.items() if
                             isinstance(v[0], LinePlot)])
        main.overlays.append(legend)

        has_img = False
        if 'image plot' in self.mainplot.plots:
            has_img = True
            imgplot = self.mainplot.plots['image plot'][0]
            self.img_data = imgplot.value
            colormap = imgplot.color_mapper
            lin_mapper = LinearMapper(range=colormap.range)
            colorbar = ColorBar(index_mapper=lin_mapper,
                                color_mapper=colormap,
                                plot=imgplot,
                                orientation='v',
                                resizable='v',
                                width=30,
                                padding=20
                                )

            colorbar.padding_top = self.mainplot.padding_top
            colorbar.padding_bottom = self.mainplot.padding_bottom

            # create a range selection for the colorbar
            range_selection = RangeSelection(component=colorbar)
            colorbar.tools.append(range_selection)
            overlay = RangeSelectionOverlay(component=colorbar,
                                            border_color="white",
                                            alpha=0.8,
                                            fill_color="lightgray")
            colorbar.overlays.append(overlay)

            # we also want to the range selection to inform the cmap plot of
            # the selection, so set that up as well
            range_selection.listeners.append(imgplot)
            #range_selection.on_trait_change(self.adjust_img, 'selection')

            # Create a container to position the plot and the colorbar
            # side-by-side
            container = HPlotContainer(use_backbuffer=True)
            container.add(self.mainplot)
            container.add(colorbar)
            container.bgcolor = "lightgray"

        firstplot = self.a_plot_with_index()
        # connect plots with range tools
        if firstplot:
            range_tool = RangeSelection(firstplot)
            firstplot.tools.append(range_tool)
            range_overlay = RangeSelectionOverlay(firstplot,
                                                  metadata_name="selections")
            firstplot.overlays.append(range_overlay)
            range_tool.on_trait_change(self._range_selection_handler,
                                       "selection")

        # add to container and fine tune spacing
        spacing = 25
        padding = 50
        width, height = (1000, 600)
        plot_container = VPlotContainer(bgcolor="lightgray",
                                        spacing=spacing,
                                        padding=padding,
                                        fill_padding=False,
                                        width=width, height=height,
                                        )
        if has_img:
            plot_container.add(self.miniplot, container)
        else:
            plot_container.add(self.miniplot, self.mainplot)

        return plot_container

    def a_plot_with_index(self):
        ''' Find first plot in data with an index or create one from img
        '''
        plots = self.miniplot.plots.values()
        indexplot = None
        imgplot = None
        for [plot] in plots:
            if isinstance(plot, LinePlot) or isinstance(plot, ScatterPlot):
                indexplot = plot

            elif isinstance(plot, CMapImagePlot):
                imgplot = plot
            if indexplot:
                break

        if not indexplot:
            if imgplot:
                array_width = imgplot.value.get_data().shape[1]
                xvalues = np.arange(array_width)
                data = self.miniplot.data
                data.set_data('default plot', xvalues)
                plot = self.miniplot.plot(('default plot'))
            else:
                pass  # 'NO SUITABLE PLOTS'

        return indexplot

    def _range_selection_handler(self, event):
        # The event obj should be a tuple (low, high) in data space
        if event is not None:
            low, high = event
            self.mainplot.index_range.low = low
            self.mainplot.index_range.high = high
        else:
            self.mainplot.index_range.set_bounds("auto", "auto")


class AddDepthLineView(HasTraits):
    ''' Defines popup window for adding new depthline'''

    # depth line instance to be edited or displays
    depth_line = Instance(DepthLine)

    # used in new depth line dialog box to apply choices to make a new line
    apply_button = Button('Apply')

    traits_view = View(
        Group(Item('depth_line'),
              'apply_button',
              ),
        buttons=['OK', 'Cancel']
    )


class ControlView(HasTraits):
    ''' Define controls and info subview with size control'''

    # list of keys for target depth lines to edit (changes if list does)
    target_choices = List(Str)

    # chosen key for depth line to edit
    line_to_edit = Str

    # frequency choices for images
    freq_choices = List()

    # selected freq for which image to view
    image_freq = Str

    # used to explicitly get edit mode
    edit = Enum('Editing', 'Not Editing')     # Button('Not Editing')

    traits_view = View(
        HGroup(
            Item('image_freq', editor=EnumEditor(name='freq_choices')),
            Item('line_to_edit',
                 editor=EnumEditor(name='target_choices'),
                 tooltip='Edit red line with right mouse button'
                 ),
            Item('edit',
                 tooltip='Toggle between "not editing" and \
                          "editing" selected line'
                 ),
            ),
        resizable=True
        )

    def _edit_default(self):
        return 'Not Editing'


class ImageAdjustView(HasTraits):
    # brightness contrast controls
    brightness = Float(0)
    contrast = Float(1)
    contrast_brightness = Property(depends_on=['brightness', 'contrast'])
    invert = Bool

    traits_view = View(
        Label('Brightness and Contrast'),
        Item('brightness', editor=RangeEditor(low=0.0, high=1.0), label='B'),
        Item('contrast', editor=RangeEditor(low=1.0, high=20.0), label='C'),
        Item('invert'),
        resizable=True
        )

    def _get_contrast_brightness(self):
        return (self.contrast, self.brightness)


class DataView(HasTraits):
    ''' Show location data as cursor moves about'''

    # latitude, longitude for current cursor
    latitude = Float(0)
    longitude = Float(0)

    # latitude, longitude for current cursor
    easting = Float(0)
    northing = Float(0)

    # depth of current mouse position
    depth = Float(0)

    traits_view = View(
        Item('latitude'),
        Item('longitude'),
        Item('_'),
        Item('easting'),
        Item('northing'),
        Item('_'),
        Item('depth'),
        resizable=True
        )


if __name__ == '__main__':
    pass
