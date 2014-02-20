""" Tools for UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports

# other imports
import numpy as np

# ETS imports
from enable.api import BaseTool, KeySpec
from traits.api import (Float, Enum, Int, Bool, Instance, Str, List, Set,
                        Property)
from chaco.api import LinePlot

#==============================================================================
# Custom Tools
#==============================================================================


class LocationTool(BaseTool):
    ''' Provides index position of cursor for selected image
    Different from Depth tool because this uses index on image in order
    to extract location values from arrays by index.  Depth can be
    taken directly from plot data.
    '''
    # index of the mouse position for given image
    image_index = Int

    def normal_mouse_move(self, event):

        index = self.component.map_index((event.x, event.y))[0]
        if index:
            self.image_index = index


class DepthTool(BaseTool):
    ''' Provides index position of cursor for selected image
    Different from Location tool because this uses data on Plot in order
    to extract depth values.  Location tool needs index.
    '''
    # index of the mouse position for given image
    depth = Float

    def normal_mouse_move(self, event):
        newx, newy = self.component.map_data((event.x, event.y))
        self.depth = newy

class InspectorFreezeTool(BaseTool):
    ''' Provides key for "freezing" line inspector tool so that cursor
    will remain in place
    '''
    tool_set = Set
    main_key = Str("f")
    modifier_key = Str("alt")
    ignore_keys = List(Str, value=['shift'])

    off_key = Instance(KeySpec)

    def _off_key_default(self):
        self.reset_off_key()
        self.on_trait_change(self.reset_off_key, ['main_key',
                                                  'modifier_key',
                                                  'ignore_keys'])
        return self.off_key

    def reset_off_key(self):
        self.off_key = KeySpec(self.main_key,
                               self.modifier_key,
                               ignore=self.ignore_keys)

    def normal_key_pressed(self, event):
        if self.off_key.match(event):
            for tool in self.tool_set:
                active = tool.is_interactive
                if active:
                    tool.is_interactive = False
                else:
                    tool.is_interactive = True


class TraceTool(BaseTool):
    """ Allows mouse update of impoundment boundary trace

    Right down mouse event will set state to edit and save a starting index
    position.  Move events will then replace values at the mouse's index
    position, filling in any missing points with lines, until the button is
    released.
    """

    event_state = Enum('normal', 'edit')

    # determines whether tool is allowed in edit state when mouse pressed
    edit_allowed = Bool(False)

    # these record last mouse position so that new position can be checked for
    # missing points -- i.e. delta_index should be 1
    last_index = Int(np.nan)
    last_y = Float(np.nan)

    depth = Float

    # when set, subsequent points will be processed for data updating.
    # when off last_y/index points will be reset to current position when
    # editing starts.  this could possibly be done with mouse down instead.
    mouse_down = Bool(False)

    target_line = Instance(LinePlot)

    # ArrayPlotData object holding all data.  This tool will change this data
    # which then updates all three freq plots at once.

    data = Property()
    # line key for this depth line.  from depth_dict, label data in data obj
    key = Str

    def _get_data(self):
        return self.target_line.container.data

    def normal_right_down(self, event):
        ''' start editing '''
        if self.edit_allowed:
            self.event_state = 'edit'
        else:
            self.event_state = 'normal'

    def edit_right_up(self, event):
        ''' finish editing'''
        self.event_state = 'normal'
        self.mouse_down = False

    # def edit_key_pressed(self, event):
    #     ''' reset '''
    #     if event.character == "Esc":
    #         self._reset()

    def fill_in_missing_pts(self, current_index, newy, ydata):
        """ Fill in missing points if mouse goes to fast to capture all

        Find linear interpolation for each array point inbetween current mouse
        position and previously captured position.
        """
        diff = np.absolute(current_index - self.last_index)
        if diff > 1:
            start = min(current_index, self.last_index)
            end = start + diff + 1
            xpts = [start, end]
            ypts = [self.last_y, newy]
            indices = range(*xpts)
            ys = np.interp(indices, xpts, ypts)
        else:
            indices = [current_index]
            ys = [newy]
        return np.array(indices), np.array(ys)

    def normal_mouse_move(self, event):
        newx, newy = self.component.map_data((event.x, event.y))
        self.depth = newy

    def edit_mouse_move(self, event):
        ''' Continuously change impound line value to the current mouse pos.

        While rt mouse button is down, this tracks the mouse movement to the
        right and changes the line value to the current mouse value at each
        index point recorded. If mouse moves too fast then the missing points
        are filled in.  If mouse is moved to the left then a straight line
        connects only the initial and final point.
        '''
        have_key = self.key != 'None'
        have_line_plot =  isinstance(self.target_line, LinePlot)

        if have_line_plot and have_key and self.edit_allowed:
            newx, newy = self.component.map_data((event.x, event.y))
            target = self.target_line
            xdata = target.index.get_data()
            current_index = np.searchsorted(xdata, newx)

            if self.mouse_down:
                ydata = target.value.get_data()
                indices, ys = self.fill_in_missing_pts(current_index,
                                                       newy, ydata)
                ydata[indices] = ys
                data_key = self.key + '_y'
                self.data.set_data(data_key, ydata)
                self.last_index = indices[-1]
                self.last_y = ys[-1]

            else:
                # save this mouse position as reference for further moves while
                # mouse_down is true.
                self.mouse_down = True
                self.last_index = current_index
                self.last_y = newy
