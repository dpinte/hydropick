#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

# 3rd party imports
import numpy as np

# ETS imports
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import PanTool, ZoomTool
from enable.component_editor import ComponentEditor
from traits.api import Float, Instance, List, Str
from traitsui.api import View, Item, ModelView, InstanceEditor, HSplit

# local imports
from hydropick.model.lake import Lake
from hydropick.ui.line_select_tool import LineSelectTool


class SurveyMapView(ModelView):
    """ View Class for working with survey line data to find depth profile.

    Uses a Survey class as a model and allows for viewing of various depth
    picking algorithms and manual editing of depth profiles.
    """
    #: XXX: this will be a survey
    model = Instance(Lake)

    # TODO: this will be a list of surveys instead of geometries
    #: Survey lines
    lines = List

    #: the plot objects for each survey line
    line_plots = List

    #: This should fix the x and y scale to maintain aspect ratio
    #: (not yet implemented)
    aspect_ratio = Float(1.0)

    #: Color to draw the shoreline
    shore_color = Str('black')

    #: Color to draw the survey lines
    line_color = Str('blue')

    #: The Chaco plot object
    plot = Instance(Plot)

    def _plot_default(self):
        plotdata = ArrayPlotData()
        plot = Plot(plotdata, auto_grid=False)
        # XXX: want to fix the pixel aspect ratio, not the window aspect ratio
        #plot.aspect_ratio = self.aspect_ratio
        for num, l in enumerate(self.model.shoreline):
            line = np.array(l.coords)
            x = line[:,0]
            y = line[:,1]
            x_key = 'x' + str(num)
            y_key = 'y' + str(num)
            plotdata.set_data(x_key, x)
            plotdata.set_data(y_key, y)
            plot.plot((x_key, y_key), color=self.shore_color, width=2.0)
        for num, l in enumerate(self.lines):
            line = np.array(l.coords)
            x = line[:,0]
            y = line[:,1]
            x_key = 'x-line' + str(num)
            y_key = 'y-line' + str(num)
            plotdata.set_data(x_key, x)
            plotdata.set_data(y_key, y)
            self.line_plots.append(plot.plot((x_key, y_key),
                                             color=self.line_color))
        plot.title = self.model.name
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        plot.tools.append(LineSelectTool(plot, line_plots=self.line_plots))
        return plot

