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
from chaco.api import (ArrayPlotData, ArrayDataSource, LinearMapper,
                       Plot, PolygonPlot, ScatterPlot, TextBoxOverlay)
from chaco.tools.api import PanTool, ZoomTool
from enable.api import BaseTool, ColorTrait
from traits.api import Bool, Dict, Float, Instance, List, on_trait_change, Property
from traitsui.api import ModelView
from pyface.tasks.api import TraitsDockPane

# local imports
from hydropick.model.i_survey import ISurvey
from hydropick.model.i_survey_line import ISurveyLine
from hydropick.ui.line_select_tool import LineSelectTool

# Constants for easy custumization of map view
# Colors are strings like 'blue' for string tuples like '(0, 0 ,255)'
# line styles are strings: 'solid', 'dot dash', 'dash', 'dot', 'long dash'
# line widths are floats

LAKE_COLOR = 'lightblue'
#: Color to draw the land
# XXX: This cannot be an arbitrary tuple, must be in enable.colors.color_table
LAND_COLOR = 'wheat'
SHORE_COLOR = 'black'
CORE_COLOR = 'red'

# attributes for lines niether approved nor selected nor current (ie default)
PENDING_LINE_COLOR = 'blue'
PENDING_LINE_WIDTH = 1.0
PENDING_LINE_STYLE = 'solid'

# selected line attributes (multiple lines selected by group or manually)
SELECTED_LINE_COLOR = 'green'
SELECTED_LINE_WIDTH = 1.0
SELECTED_LINE_STYLE = 'solid'

# current line attributes (line being edited: one only)
CURRENT_LINE_COLOR = 'red'
CURRENT_LINE_WIDTH = 2.0
CURRENT_LINE_STYLE = 'solid'

# status attributes (applied after selected or current)
BAD_LINE_STYLE = 'dot'
BAD_LINE_WIDTH = 1.0
BAD_LINE_COLOR = 'grey'

APPROVED_LINE_STYLE = 'dash'
APPROVED_LINE_WIDTH = 1.0
APPROVED_LINE_COLOR = 'black'

# controls display of current survey line name in map view
TEXTBOX_COLOR = 'red'
TEXTBOX_POSITION = 'ul'
TEXTBOX_BG_COLOR = 'white'

class MapPlot(Plot):
    """ A subclass of Plot to allow setting of x- and y- scale to be constant.

    A bit of a kludge to make it is run only once for a plot.
    Ideally this would change the aspect ratio on resize events as well,
    but that will take more work to make sure it isn't called recursively.
    """

    #: only do this once for a given plot
    aspect_ratio_set = Bool(False)

    def _update_mappers(self):
        super(MapPlot, self)._update_mappers()
        if not self.aspect_ratio_set:
            self._update_aspect_ratio()

    def _update_aspect_ratio(self):
        x_max = self.index_mapper.range.high
        x_min = self.index_mapper.range.low
        y_max = self.value_mapper.range.high
        y_min = self.value_mapper.range.low
        self.aspect_ratio = (self.index_mapper.screen_bounds[1] /
                             self.value_mapper.screen_bounds[1])
        data_aspect_ratio = (x_max - x_min) / (y_max - y_min)
        if data_aspect_ratio == self.aspect_ratio:
            return
        elif data_aspect_ratio > self.aspect_ratio:
            # expand data range in y-direction to match
            y_center = (y_max + y_min) / 2
            y_max_new = y_center + (x_max - x_min) / (2 * self.aspect_ratio)
            y_min_new = y_center - (x_max - x_min) / (2 * self.aspect_ratio)
            self.value_mapper.range.high = y_max_new
            self.value_mapper.range.low = y_min_new
        else:
            # expand data range in x-direction to match
            x_center = (x_max + x_min) / 2
            x_max_new = x_center + (y_max - y_min) * self.aspect_ratio / 2
            x_min_new = x_center - (y_max - y_min) * self.aspect_ratio / 2
            self.index_mapper.range.high = x_max_new
            self.index_mapper.range.low = x_min_new
        self.aspect_ratio_set = True


class SurveyMapView(ModelView):
    """ View Class for working with survey line data to find depth profile.

    Uses a Survey class as a model and allows for viewing of various depth
    picking algorithms and manual editing of depth profiles.
    """
    #: The current survey
    model = Instance(ISurvey)

    #: Survey lines
    survey_lines = Property(List)

    bad_lines = Property(List)
    approved_lines = Property(List)

    def _get_bad_lines(self):
        bad = []
        for line in self.survey_lines:
            if line.status == 'bad':
                bad.append(line.name)
        return bad

    def _get_approved_lines(self):
        approved = []
        for line in self.survey_lines:
            if line.status == 'approved':
                approved.append(line.name)
        return approved

    def _get_survey_lines(self):
        return self.model.survey_lines

    #: the plot objects for each survey line
    line_plots = Dict

    map_pane = Instance(TraitsDockPane)

    line_select_tool = Instance(BaseTool)

    #: distance tolerance in data units on map (feet by default)
    tol = Float(200)

    #: proxy for the task's current survey line
    current_survey_line = Instance(ISurveyLine)

    #: reference to the task's selected survey lines
    selected_survey_lines = List(Instance(ISurveyLine))

    @on_trait_change('current_survey_line, selected_survey_lines, bad_lines')
    def _set_line_colors(self):
        for name, plot in self.line_plots.iteritems():
            lp = plot[0]
            if self.current_survey_line and \
                                    (name == self.current_survey_line.name):
                lp.color = self.current_line_color
                lp.line_width = CURRENT_LINE_WIDTH
                lp.line_style = CURRENT_LINE_STYLE
            elif name in [line.name for line in self.selected_survey_lines]:
                lp.color = self.selected_line_color
                lp.line_width = SELECTED_LINE_WIDTH
                lp.line_style = SELECTED_LINE_STYLE
            else:
                lp.color = self.line_color
            if name in self.bad_lines:
                lp.line_style = BAD_LINE_STYLE
                lp.line_width = BAD_LINE_WIDTH
                lp.color = BAD_LINE_COLOR
            elif name in self.approved_lines:
                lp.line_style = APPROVED_LINE_STYLE
                lp.line_width = APPROVED_LINE_WIDTH
                lp.color = APPROVED_LINE_COLOR

    #: Color to draw the lake
    lake_color = ColorTrait(LAKE_COLOR)

    #: Color to draw the land
    # XXX: This cannot be an arbitrary tuple, must be in enable.colors.color_table
    land_color = ColorTrait(LAND_COLOR)

    #: Color to draw the shoreline
    shore_color = ColorTrait(SHORE_COLOR)

    #: Color to draw the core locations
    core_color = ColorTrait(CORE_COLOR)

    #: Color to draw the survey lines
    line_color = ColorTrait(PENDING_LINE_COLOR)

    #: Color to draw the selected survey lines
    selected_line_color = ColorTrait(SELECTED_LINE_COLOR)

    #: Color to draw the survey lines
    current_line_color = ColorTrait(CURRENT_LINE_COLOR)

    #: text overlay to see names of clicked lines (mouseover may be better)
    text_overlay = Instance(TextBoxOverlay)

    #: The Chaco plot object
    plot = Instance(Plot)

    def _plot_default(self):
        plotdata = ArrayPlotData()
        plot = MapPlot(plotdata,
                       auto_grid=False,
                       bgcolor=self.land_color)
        plot.x_axis.visible = False
        plot.y_axis.visible = False
        plot.padding = (0, 0, 0, 0)
        plot.border_visible = False
        index_mapper = LinearMapper(range=plot.index_range)
        value_mapper = LinearMapper(range=plot.value_range)
        if self.model.lake is not None:
            line_lengths = [l.length for l in self.model.lake.shoreline]
            idx_max = line_lengths.index(max(line_lengths))
            for num, l in enumerate(self.model.lake.shoreline):
                line = np.array(l.coords)
                x = line[:,0]
                y = line[:,1]
                # assume that the longest polygon is lake, all others islands
                if num == idx_max:
                    color = self.lake_color
                else:
                    color = self.land_color
                polyplot = PolygonPlot(index=ArrayDataSource(x),
                                       value=ArrayDataSource(y),
                                       edge_color=self.shore_color,
                                       face_color=color,
                                       index_mapper=index_mapper,
                                       value_mapper=value_mapper)
                plot.add(polyplot)
        for num, line in enumerate(self.survey_lines):
            coords = np.array(line.navigation_line.coords)
            x = coords[:,0]
            y = coords[:,1]
            x_key = 'x-line' + str(num)
            y_key = 'y-line' + str(num)
            plotdata.set_data(x_key, x)
            plotdata.set_data(y_key, y)
            self.line_plots[line.name] = plot.plot((x_key, y_key),
                                                color=self.line_color,
                                                line_width=PENDING_LINE_WIDTH,
                                                line_style=PENDING_LINE_STYLE)
        for core in self.model.core_samples:
            x, y = core.location
            scatterplot = ScatterPlot(index=ArrayDataSource([x]),
                                       value=ArrayDataSource([y]),
                                       marker='circle',
                                       color=self.core_color,
                                       outline_color=self.core_color,
                                       index_mapper=index_mapper,
                                       value_mapper=value_mapper)
            plot.add(scatterplot)
        self._set_line_colors()
        if self.model.lake is not None:
            x_min, y_min, x_max, y_max = self.model.lake.shoreline.bounds
            index_mapper.range.high = x_max
            index_mapper.range.low = x_min
            value_mapper.range.high = y_max
            value_mapper.range.low = y_min
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        self.line_select_tool = LineSelectTool(plot, line_plots=self.line_plots)
        # single click in map sets 'select point':  toggle in selected lines
        self.line_select_tool.on_trait_event(self.select_point, 'select_point')
        # double click in map sets 'current point': change current survey line
        self.line_select_tool.on_trait_event(self.current_point, 'current_point')
        plot.tools.append(self.line_select_tool)
        line_name_text = TextBoxOverlay(component=plot,
                                        text=self.get_current_line_name(),
                                        text_color=TEXTBOX_COLOR,
                                        align=TEXTBOX_POSITION,
                                        bgcolor=TEXTBOX_BG_COLOR
                                        )
        plot.overlays.append(line_name_text)
        self.text_overlay = line_name_text
        return plot

    def select_point(self, event):
        ''' single click in map toggles line selection status in selected lines
        '''
        p = Point(event)
        for line in self.survey_lines:
            if line.navigation_line.distance(p) < self.tol:
                self._select_line(line)

    def current_point(self, event):
        ''' double click in map sets line as current survey line (for editing)
        '''
        p = Point(event)
        for line in self.survey_lines:
            if line.navigation_line.distance(p) < self.tol:
                self.current_survey_line = line
                # never want to set more than one line to current so break now
                break

    def _select_line(self, line):
        print 'select', line.name
        self.text_overlay.text = line.name
        self.text_overlay.invalidate_and_redraw()
        if line in self.selected_survey_lines:
            self.selected_survey_lines.remove(line)
        else:
            self.selected_survey_lines.append(line)

    def get_current_line_name(self):
        if self.current_survey_line:
            name = self.current_survey_line.name
        else:
            name = 'No line clicked'
        return name
