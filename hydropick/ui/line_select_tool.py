#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

# ETS imports
from enable.api import BaseTool
from traits.api import Event


class LineSelectTool(BaseTool):
    """ A tool for selecting navigation lines.

    This tool dispatches events with clicked locations.  The work for
    choosing which lines to select is done in the survey map view.
    """

    #: select a new line
    select_point = Event

    #: make a new line the current one
    current_point = Event

    def normal_left_down(self, event):
        """ Dispatch an event with clicked location """
        plot = self.component
        x = plot.index_mapper.map_data(event.x)
        y = plot.value_mapper.map_data(event.y)
        self.select_point = (x, y)

    def normal_left_dclick(self, event):
        """ Dispatch an event with double-clicked location """
        plot = self.component
        x = plot.index_mapper.map_data(event.x)
        y = plot.value_mapper.map_data(event.y)
        self.current_point = (x, y)
