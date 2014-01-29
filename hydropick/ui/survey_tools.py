""" Tools for UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports

# other imports
import numpy as np

# ETS imports
from enable.api import BaseTool
from traits.api import Float, Enum, Int, Bool, Instance
from chaco.api import LinePlot

#==============================================================================
# Custom Tools
#==============================================================================


class LocationTool(BaseTool):
    ''' Provides index position of cursor for selected image
    '''

    image_index = Int

    def normal_mouse_move(self, event):
        index = self.component.map_index((event.x, event.y))[0]
        if index:
            self.image_index = index
        event.handled = False


class TraceTool(BaseTool):
    """ Allows mouse update of impoundment boundary trace

    Right down mouse event will set state to edit and save a starting index
    position.  Move events will then replace values at the mouse's index
    position, filling in any missing points with lines, until the button is
    released.
    """

    event_state = Enum('normal', 'edit')
    # these record last mouse position so that new position can be checked for
    # missing points -- i.e. delta_index should be 1
    last_index = Int(np.nan)
    last_y = Float(np.nan)

    depth = Float
    # when set, subsequent points will be processed for data updating.
    mouse_down = Bool(False)

    target_line = Instance(LinePlot)

    def normal_right_down(self, event):
        self.event_state = 'edit'

    def edit_right_up(self, event):
        self.event_state = 'normal'
        self.mouse_down = False

    def edit_key_pressed(self, event):
        # saw this in an example but it doesn't seem to do anything.
        if event.character == "Esc":
            self._reset()

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

        if isinstance(self.target_line, LinePlot):
            newx, newy = self.component.map_data((event.x, event.y))
            target = self.target_line
            xdata = target.index.get_data()
            current_index = np.searchsorted(xdata, newx)

            if self.mouse_down:
                ydata = target.value.get_data()
                indices, ys = self.fill_in_missing_pts(current_index,
                                                       newy, ydata)
                ydata[indices] = ys
                target.value.set_data(ydata)
                self.last_index = indices[-1]
                self.last_y = ys[-1]

            else:
                # save this mouse position as reference for further moves while
                # mouse_down is true.
                self.mouse_down = True
                self.last_index = current_index
                self.last_y = newy

                
