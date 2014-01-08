#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

# 3rd party imports
import numpy as np
from shapely.geometry import shape

# ETS imports
from chaco.api import Plot, ArrayPlotData
from chaco.tools.api import PanTool, ZoomTool
from enable.api import BaseTool
from enable.component_editor import ComponentEditor
from traits.api import Float, HasTraits, Instance, List, Str
from traitsui.api import View, Item

# local imports
from hydropick.model.lake import Lake


class LineSelectTool(BaseTool):
    """ A tool for selecting navigation lines.

    Currently very crude and only changes line color.  In the future
    this will actually be connected to selections in application.
    """

    #: distance tolerance in data units on map (feet by default)
    tol = Float(100.0)

    # ughly
    line_plots = List

    def _select(self, token, append=True):
        pass

    def _deselect(self, token, append=True):
        pass

    def normal_left_down(self, event):
        """ Select a line if it is within 100 ft """
        tol2 = self.tol ** 2
        plot = self.component
        x = plot.index_mapper.map_data(event.x)
        y = plot.value_mapper.map_data(event.y)
        for lp, in self.line_plots:
            x_line = lp.index.get_data()
            y_line = lp.value.get_data()
            dist = np.min((x_line - x)**2 + (y_line - y)**2)
            if dist < tol2:
                print 'Select', lp, x, y
                # FIXME: This is an ugly way to decide if selected
                if lp.color == 'blue':
                    lp.color = 'red'
                    self._select(lp)
                else:
                    lp.color = 'blue'
                    self._deselect(lp)


class LakePlot(HasTraits):

    #: Lake to plot
    lake = Instance(Lake)

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
        for num, l in enumerate(self.lake.shoreline):
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
        plot.title = lake.name
        plot.tools.append(PanTool(plot))
        plot.tools.append(ZoomTool(plot))
        plot.tools.append(LineSelectTool(plot, line_plots=self.line_plots))
        return plot

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       width=600,
                       height=400,
                       resizable=True,
                       title='Lake plot')


if __name__ == '__main__':
    import os
    import fiona

    cwd = os.path.dirname(__file__)
    shpfile = os.path.join(cwd, 'test', 'files', 'shoreline1083.shp')
    name = 'Somerville'
    lake = Lake(name=name, shoreline_file=shpfile)
    line_file = os.path.join(cwd, 'test', 'files', 'Somerville-lines.json')
    with fiona.open(line_file) as f:
        rec = f.next()
        lines = list(shape(rec['geometry']))
    plot = LakePlot(lake=lake, lines=lines)
    plot.configure_traits()
