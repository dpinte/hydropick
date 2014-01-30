#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

# 3rd party imports
import numpy as np
from shapely.geometry import Point

# ETS imports
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import PanTool, ZoomTool
from enable.api import BaseTool
from traits.api import Dict, Float, Instance, List, on_trait_change, Property, Str
from traitsui.api import ModelView
from pyface.tasks.api import TraitsDockPane

# local imports
from hydropick.model.i_survey import ISurvey
from hydropick.model.i_survey_line import ISurveyLine
from hydropick.ui.line_select_tool import LineSelectTool


class SurveyMapView(ModelView):
    """ View Class for working with survey line data to find depth profile.

    Uses a Survey class as a model and allows for viewing of various depth
    picking algorithms and manual editing of depth profiles.
    """
    #: The current survey
    model = Instance(ISurvey)

    #: Survey lines
    survey_lines = Property(List)

    def _get_survey_lines(self):
        return self.model.survey_lines

    #: the plot objects for each survey line
    line_plots = Dict

    map_pane = Instance(TraitsDockPane)

    line_select_tool = Instance(BaseTool)

    #: distance tolerance in data units on map (feet by default)
    tol = Float(100)

    #: proxy for the task's current survey line
    current_survey_line = Instance(ISurveyLine)

    #: reference to the task's selected survey lines
    selected_survey_lines = List(Instance(ISurveyLine))

    @on_trait_change('current_survey_line, selected_survey_lines')
    def _set_line_colors(self):
        for name, plot in self.line_plots.iteritems():
            lp = plot[0]
            if self.current_survey_line and name == self.current_survey_line.name:
                lp.color = self.current_line_color
            elif name in [line.name for line in self.selected_survey_lines]:
                lp.color = self.selected_line_color
            else:
                lp.color = self.line_color

    #: This should fix the x and y scale to maintain aspect ratio
    #: (not yet implemented)
    aspect_ratio = Float(1.0)

    #: Color to draw the shoreline
    shore_color = Str('black')

    #: Color to draw the survey lines
    line_color = Str('blue')

    #: Color to draw the selected survey lines
    selected_line_color = Str('green')

    #: Color to draw the survey lines
    current_line_color = Str('red')

    #: The Chaco plot object
    plot = Property(Instance(Plot), depends_on='model')

    def _get_plot(self):
        plotdata = ArrayPlotData()
        plot = Plot(plotdata, auto_grid=False)
        # XXX: want to fix the pixel aspect ratio, not the window aspect ratio
        #plot.aspect_ratio = self.aspect_ratio
        if self.model.lake is not None:
            for num, l in enumerate(self.model.lake.shoreline):
                line = np.array(l.coords)
                x = line[:,0]
                y = line[:,1]
                x_key = 'x' + str(num)
                y_key = 'y' + str(num)
                plotdata.set_data(x_key, x)
                plotdata.set_data(y_key, y)
                plot.plot((x_key, y_key), color=self.shore_color, width=2.0)
        for num, line in enumerate(self.survey_lines):
            coords = np.array(line.navigation_line.coords)
            x = coords[:,0]
            y = coords[:,1]
            x_key = 'x-line' + str(num)
            y_key = 'y-line' + str(num)
            plotdata.set_data(x_key, x)
            plotdata.set_data(y_key, y)
            self.line_plots[line.name] = plot.plot((x_key, y_key),
                                                   color=self.line_color)
        plot.title = self.model.name
        self._set_line_colors()
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        self.line_select_tool = LineSelectTool(plot, line_plots=self.line_plots)
        self.line_select_tool.on_trait_event(self.select_point, 'select_point')
        self.line_select_tool.on_trait_event(self.current_point, 'current_point')
        plot.tools.append(self.line_select_tool)
        return plot

    def select_point(self, event):
        p = Point(event)
        for line in self.survey_lines:
            if line.navigation_line.distance(p) < self.tol:
                self._select_line(line)

    def current_point(self, event):
        p = Point(event)
        for line in self.survey_lines:
            if line.navigation_line.distance(p) < self.tol:
                self._current_line(line)
                # never want to set more than one line to current
                break

    def _select_line(self, line):
        print 'select', line.name
        if line in self.selected_survey_lines:
            self.selected_survey_lines.remove(line)
        else:
            self.selected_survey_lines.append(line)

    def _current_line(self, line):
        print 'set current to', line.name
        self.current_survey_line = line
