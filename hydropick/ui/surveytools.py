""" Tools for UI building excercise to prepare for TWDB sonar plotting project


"""
# Std lib imports

# other imports
import numpy as np

# ETS imports
from enable.api import BaseTool
from traits.api import Float, Enum, Int, Bool, Instance, TraitError, Any
from chaco.api import  LinePlot, CMapImagePlot
#==============================================================================
# Custom Tools
#==============================================================================
class LocationTool(BaseTool):
    image_index = Int
    def normal_mouse_move(self,event):
        self.image_index = self.component.map_index((event.x, event.y))[0]
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

    def normal_right_down(self,event):
        self.event_state = 'edit'

    def normal_right_up(self,event):
        self.event_state = 'normal'
        self.mouse_down = False

    def edit_right_down(self,event):
        self.event_state = 'edit'

    def edit_right_up(self,event):
        self.event_state = 'normal'
        self.mouse_down = False

    def edit_key_pressed(self,event):
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
            xpts = [start,end]
            ypts = [self.last_y, newy]
            indices = range(*xpts)
            ys = np.interp(indices,xpts,ypts)
        else:
            indices = [current_index]
            ys = [newy]
        return np.array(indices), np.array(ys)

    def normal_mouse_move(self, event):
        newx, newy = self.component.map_data( (event.x, event.y))
        self.depth = newy
        
    def edit_mouse_move(self,event):
        ''' Continuously change the impound line value to the current mouse pos.

        While rt mouse button is down, this tracks the mouse movement to the
        right and changes the line value to the current mouse value at each
        index point recorded. If mouse moves too fast then the missing points
        are filled in.  If mouse is moved to the left then a straight line
        connects only the initial and final point.
        '''

        if isinstance(self.target_line, LinePlot):

            data = self.component.data
            newx, newy = self.component.map_data( (event.x, event.y))
            print newx, newy,(event.x, event.y)
            target = self.target_line
            xdata = target.index.get_data()
            current_index = np.searchsorted(xdata,newx)


            if self.mouse_down:
                ydata = target.value.get_data()
                #           # ydata = data.get_data("impound_1_Y")
                indices, ys = self.fill_in_missing_pts(current_index, newy, ydata)
                ydata[indices] = ys
                target.value.set_data(ydata)
                #           # data.set_data("impound_1_Y", ydata)
                self.last_index = indices[-1]
                self.last_y = ys[-1]

            else:
                # save this mouse position as reference for further moves while
                # mouse_down is true.

                self.mouse_down = True
                self.last_index = current_index
                self.last_y = newy


def build_histogram_plot2(xs, ys, range_selection_tool=True):
    """ Generic BarPlot maker, with a range selection tool attached.
    """
    plot = OverlayPlotContainer(bgcolor = "white", auto_size=True)
    x_source = ArrayDataSource(xs)
    y_source = ArrayDataSource(ys)

    # Create the index range
    index_range = DataRange1D(x_source)
    index_range.tight_bounds = False
    x_mapper = LinearMapper(range=index_range)

    # Create the value range
    value_range = DataRange1D(y_source)
    value_range.tight_bounds = False
    y_mapper = LinearMapper(range=value_range)

    delta = xs[1] - xs[0]
    x_mapper.range.low = xs[0] - delta / 2.
    x_mapper.range.high = xs[-1] + delta / 2.

    y_mapper.range.high *= 1.05

    plot = BarPlot(
            index = x_source,
            value = y_source,
            index_mapper = x_mapper,
            value_mapper = y_mapper,
            fill_color = 'blue',
            bar_width = delta,
            padding_right = 1,
            padding_left = 45,
            padding_top = 0,
            padding_bottom = 20,
        )
    add_axes(plot)
    plot.tools.append(RangeSelection(plot))
    plot.overlays.append(RangeSelectionOverlay(component=plot))
    return plot, x_source, y_source

def compute_hist_data(self, field_name):
    """ Compute the histogram data for any field (threshold or selected field.).

    FIXME: This should reuse get_field_data.
    """
    data = self.model.get_data_for_field(field_name)
    if data is None:
        raise ValueError("%s isn't a known variable" % field_name)
    if data.ndim == 2:
        data = data[self.time_slice, :]
    ys, bin_edges = np.histogram(data, bins=self.n_hist_bin)
    xs = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    return xs, ys
