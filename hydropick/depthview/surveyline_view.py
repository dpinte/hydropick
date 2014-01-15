#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#


# Std lib imports

# other imports
import numpy as np

# ETS imports
from enable.api import ComponentEditor
from traits.api import Instance, Enum, DelegatesTo, Str, Property, Dict, List, Tuple, Int

from traitsui.api import ModelView, View, Item, ToolBar, EnumEditor, Group, HGroup,HGroup,UItem,InstanceEditor, VGroup, CheckListEditor, HSplit
from traitsui.menu import Action, OKCancelButtons, StandardMenuBar
from chaco.api import Plot, ArrayPlotData, jet, PlotAxis, create_scatter_plot,\
                        create_line_plot, LinePlot, Legend, PlotComponent, Greys

from chaco.tools.api import PanTool, ZoomTool, LegendTool
from pyface.api import ImageResource

# Local imports
from surveydatasession import SurveyDataSession
from surveytools import TraceTool
from surveyviews import ControlView, PlotView, BigView, InstanceUItem, PlotContainer

class SurveyLineView(ModelView):
    """ View Class for working with survey line data to find depth profile.

    Uses a Survey class as a model and allows for viewing of various depth
    picking algorithms and manual editing of depth profiles.
    """

    #==========================================================================
    # Traits Attributes
    #==========================================================================

    # Data model is Survey class containing core data, SDI survey data, lake data,
    # and links to algorithms.
    model = Instance(SurveyDataSession)

    # Defines view for all the plots.  Place beside control view
    plot_container = Instance(PlotContainer)

    # Defines view for all the plots.  Place beside control view
    control_view = Instance(ControlView)

    # Dictionary of plots kept for legend and for tools.  Will contain all depth lines at least.
    # This contains components as opposed to the depth_dict{str:array} in the model.
    plot_dict = Dict(Str, PlotComponent, value={})

    # Custom tool for editing depth lines
    trace_tool = Instance(TraceTool)

    # List of which lines are visible in plots
    visible_lines = List([])

    # plotdata is the ArrayPlotData instance holding the plot data.
    # for now it contains 1 image and multiple line plots for depths
    plotdata = Instance(ArrayPlotData)

    # Pair of combined plots:  Main for editing; mini for scanning
    mainplot = Instance(Plot)
    miniplot = Instance(Plot)
    mini_height = Int(100)

    #==========================================================================
    # Define View
    #==========================================================================

    traits_view = View(
                      Item('_'),
                      HSplit(
                          InstanceUItem('control_view',
                                        width=150),
                          InstanceUItem('plot_container',
                                        width=900, height=700),
                          show_border=True
                          ),
                      resizable=True,
                      )

    #==========================================================================
    # Defaults
    #==========================================================================

    def _plot_dict_default(self):
        ''' To be filled by plot methods'''
        return {}

    def _plot_container_default(self):
        linedict = self.model.depth_dict
        self.mainplot = self.make_plot()
        self.miniplot = self.make_plot(height=self.mini_height)
        contnr = PlotContainer(mainplot= self.mainplot, miniplot= self.miniplot)
        if self.model.depth_dict:
            self.add_lines(**self.model.depth_dict)
        if self.model.frequencies:
            self.add_images(**self.model.frequencies)
        return contnr

    def _control_view_default(self):
        cv = ControlView(target_choices=self.model.target_choices,
                         line_to_edit=self.model.selected_target,
                         visible_lines=self.visible_lines,
                         freq_choices=self.model.freq_choices,
                         image_freq=self.model.selected_freq
                         )
        cv.visible_lines = self.model.target_choices
        cv.image_freq = self.model.selected_freq

        cv.on_trait_change(self.select_line, name='visible_lines')
        cv.on_trait_change(self.change_target, name='line_to_edit')
        cv.on_trait_change(self.change_image, name='image_freq')
        return cv

    # def _visible_lines_default(self):
    #     ''' If lines present set all as visible'''
    #     for line in self.model.depth_dict:
            # self.visible_lines.append(line)


    # def _plot_cont_default(self):
    #     ''' Create plots and add to container
    #     '''

    #     plots = Plot(self.plotdata)
    #     #import ipdb; ipdb.set_trace()

    #     #plots.img_plot('No_data', colormap=jet, origin='top left')

    #     # Add tools
    #     plots.tools.append(PanTool(plots))
    #     plots.tools.append(ZoomTool(plots))

    #     return plots

    def _plotdata_default(self):
        #return ArrayPlotData(No_data=np.zeros([2,2]))
        if self.model.x_array.any():
            return ArrayPlotData(x_array=self.model.x_array)
        else:
            return ArrayPlotData()

    def _trace_tool_default(self):
        tool =  TraceTool(self.mainplot)
        self.mainplot.tools.append(tool)
        return tool
    # def _plotview_default(self):
    #pv = PlotView(plot=self.plot_cont)
    #   return pv                         #
    #
    # def _controlview_default(self):
    #     cv = ControlView(freqs=self.plotted_freqs, choices=self.freq_choices,
    #                      survey_binary=self.model.survey_binary)
    #     return cv


    #==========================================================================
    # Helper functions
    #==========================================================================

    def add_lines(self,**kw):
        ''' Take arbitrary number of key=array pairs.
        Adds them to
        self.plotdata then self.depth_dict,
        adds them to mainplot and miniplot,
        adds the comonents to self.plot_dict'''
        for key, array in kw.items():
            self.plotdata.set_data(key, array)
        self.model.depth_dict.update(kw)
        self.update_main_mini_lines(kw.keys())


    def add_images(self,**kw):
        '''
        '''
        for key, array in kw.items():
            self.plotdata.set_data(key, array)
        self.model.frequencies.update(kw)
        imagelist = [kw.keys()[0]]
        self.update_main_mini_image(imagelist)

    def make_plot(self, height=None, plotdict=True):
        ''' Creates one Plot instance with all depthlines and one image plot.
        Used for mainplot and miniplot to make identical plots apart from
        height.  plotdict=True value tells it to create new plot_dict.
        Takes linedict of {str:array} for line plots.
        '''

        # if plotdict:
        #     newdict = {}

        # # add lines to plotdata -----------------------------------------------
        # plotdata = ArrayPlotData(**linedict)
        # for key in self.model.frequencies:
        #     plotdata.set_data(key, self.model.frequencies[key])

        # plot lines -----------------------------------------------------------
        # set origin to top left to have positive depths go down.

        plot = Plot(self.plotdata,
                    border_visible=True,
                    bgcolor="white",
                    padding=0,
                    origin ='top left'
                    )
        if height:
            plot.height=height
            plot.resizable='h'

        # for key in linedict:
        #     # may want to add rotating color generator
        #     newline = plot.plot((key), color='blue', name=key)
        #     if plotdict:
        #         newdict[key] = newline[0]

        # plot images -----------------------------------------------------------
        #
        # if self.freq_selected:

        # if plotdict:
        #     self.plot_dict = newdict
        return plot

    def update_main_mini_lines(self, keylist=[]):
        ''' Add specified lineplots already in self.plotdata to both plots
        Assumes x_array from model.x_array is already in plotdata as well.
        '''
        main = self.mainplot
        mini = self.miniplot
        for key in keylist:
            newplot = main.plot(('x_array',key), color='blue', name=key)
            self.plot_dict[key] = newplot[0]
            mini.plot(('x_array',key), color='blue', name=key)


    def update_main_mini_image(self, keylist=[], remove=None):
        ''' Add specified image plots from self.plotdata to both plots.
        Should be done after lineplots to set plot axis ranges automatically
        '''
        main = self.mainplot
        mini = self.miniplot
        for key in keylist:
            print 'plotting',key
            newplot = main.img_plot(key, colormap=Greys,
                                    xbounds=self.model.xbounds,
                                    ybounds=self.model.ybounds,
                                    name=key)
            self.plot_dict[key] = newplot[0]
            mini.img_plot(key, colormap=Greys,
                          xbounds=self.model.xbounds,
                          ybounds=self.model.ybounds,
                          name=key)
        if remove:
            print 'in remove',remove
            print main.plots
            print main.components
            component1 = mini.plots.pop(remove)[0]
            component2 = main.plots.pop(remove)[0]
            print main.plots
            print main.components
            print component1, component2
            # main.remove(component1)
            # mini.remove(component2)
            # print main.plots
            # print main.components
        self.mainplot.invalidate_and_redraw()




    def update_plots(self):
        ''' Create plots and add to container. Run when new plot is added or
        new survey is selected.
        '''

        print "updating plots"
        # fills self.plotdata with ArrayPlotData instance
        self.set_plotdata()
        # plots = Plot(self.plotdata,origin='top left')
        # #import ipdb; ipdb.set_trace()

        # # Plot an arbitrary image in frequencies dict.
        if self.model.frequencies:
            self.freq_selected = self.model.frequencies.keys()[0]
        else:
            self.freq_selected = 'No_data'

        self.ybounds=(0, 2*self.model.ymax)
        # plots.img_plot(freq, colormap=Greys,# origin='top left',
        #             ybounds=ybounds)


        linedict = self.model.depth_dict
        self.mainplot = self.make_plot(linedict)
        self.miniplot = self.make_plot(linedict, height=100, plotdict=False)
        # self.mainplot = mainplot
        # self.miniplot = miniplot
        # print self.mainplot
        print self.miniplot
        #import ipdb; ipdb.set_trace()
        contnr = PlotContainer(mainplot= self.mainplot, miniplot= self.miniplot)
        #contnr = PlotContainer(mainplot= self.mainplot, miniplot= self.miniplot)
        #contnr = PlotContainer(mainplot=self.mainplot, miniplot=self.miniplot)

        # for key, data in self.model.depth_dict.items():
        #     print key
        #     print data
        #     a_plot = plots.plot((key), type='line',
        #                         name=key,)
        #     self.plot_dict[key] = a_plot[0]
        self.trace_tool = TraceTool(self.mainplot, target_line=self.target_line)
        self.mainplot.tools.append(self.trace_tool)

        #self.plot_cont = plots
        self.contnr = contnr
        #import ipdb; ipdb.set_trace()


    #==========================================================================
    # Get/Set methods
    #==========================================================================
    def load_plotdata(self):
        ''' Assemble the relevant starting data in ArrayPlotData array

        '''
        # First 2D arrays for all frequenciess to plotdata from frequencies dict
        self.plotdata = ArrayPlotData(**self.model.frequencies)

        # Then add any depth line data that may exist
        for key,value in self.model.depth_dict.items():
            self.plotdata.set_data(key,value)
            self.xbounds = (0,len(value))
            self.ybounds = (np.min(value),np.max(value))

    def _get_target_line(self):
        # returns actual line_plot opject currently selected
        currentline = self.plot_dict.get(self.model.selected_target, None)
        return currentline

    # def _get_controlview(self):
    #     t_choices = self.target_choices
    #     print 'choices = ', t_choices,self.freq_choices
    #     cv = ControlView(freqs=self.plotted_freqs, choices=self.freq_choices,
    #                      current_target=self.current_target_name,
    #                      target_choices=self.target_choices)
    #     cv.on_trait_change(self.select_line, name='freqs')
    #     cv.on_trait_change(self.change_target, name='current_target')
    #     return cv
    # #
    #==========================================================================
    # Notifications
    #==========================================================================
    # def _datafile_changed(self,new):
    #     print 'datafile changed'
    #     self.update_plots()

    # def _current_target_name_changed(self,new):
    #     # update trace tool target line attribute.
    #     self.trace_tool.target_line = self.target_line

    def change_target(self, object, name, old, new):
        # update trace tool target line attribute.
        print 'new target name is ', new
        new_target_line = self.plot_dict[new]
        new_target_line.color = 'red'
        old_target_line = self.plot_dict.get(old, None)
        if old_target_line:
            old_target_line.color = 'blue'
        self.trace_tool.target_line = new_target_line

    def change_image(self, object, name, old, new):
        # update trace tool target line attribute.
        print 'new image name is ', new
        if old in self.plot_dict:
            self.update_main_mini_image([new],remove=old)
        else:
            self.update_main_mini_image([new])

    def select_line(self,object, name, old, new):
        print 'visible depthlines changed'
        for name in self.model.depth_dict:
            this_plot = self.mainplot.plots[name][0]
            if name in new:
                this_plot.visible=True
            else:
                this_plot.visible=False
        self.mainplot.invalidate_and_redraw()


if __name__ == "__main__":
    datasession = SurveyDataSession()
    print 'datasession object=',datasession
    print 'starting GUI'
    window = SurveyLineView(model=datasession)
    window.configure_traits()

    #import ipdb; ipdb.set_trace()
