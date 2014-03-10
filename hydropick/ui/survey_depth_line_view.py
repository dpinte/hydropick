#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from copy import deepcopy
import logging
import numpy as np

# ETS imports
from traits.api import (Instance, Str, Property, HasTraits, Int, List,
                        on_trait_change, Button, Bool, Supports, Dict)
from traitsui.api import (View, VGroup, HGroup, Item, UItem, EnumEditor,
                          TextEditor, ListEditor)

# Local imports
from ..model.depth_line import DepthLine
from ..model.i_survey_line_group import ISurveyLineGroup
from ..model.i_survey_line import ISurveyLine
from .survey_data_session import SurveyDataSession
from .survey_views import MsgView

logger = logging.getLogger(__name__)

ARG_TOOLTIP = 'comma separated keyword args -- x=1,all=True,s="Tom"'
UPDATE_ARRAYS_TOOLTIP = \
    'updates array data in form but does not apply to line'
APPLY_TOOLTIP = \
    'applies current setting to line, but does not update data'


class DepthLineView(HasTraits):
    """ View Class for working with survey line data to find depth profile.

    Uses a Survey class as a model and allows for viewing of various depth
    picking algorithms and manual editing of depth profiles.
    """

    #==========================================================================
    # Traits Attributes
    #==========================================================================

    # current data session with relevant info for the current line
    data_session = Instance(SurveyDataSession)

    # name of current line in editor
    survey_line_name = Property(depends_on=['data_session']
                                )

    # list of available depth lines extracted from survey line
    depth_lines = Property(depends_on=['data_session',
                                       'data_session.depth_lines_updated']
                           )

    # name of depth_line to view chosen from pulldown of all available lines.
    selected_depth_line_name = Str

    # name of hdf5_file for this survey in case we need to load survey lines
    hdf5_file = Str

    # current depth line object
    model = Instance(DepthLine)

    # set of arguments for algorithms.  Assume keyword.  makes dict
    args = Property(Str, depends_on=['model.args', 'model'])

    # arrays to plot
    index_array_size = Property(Int, depends_on=['model.index_array, model'])
    depth_array_size = Property(Int, depends_on=['model.depth_array, model'])

    # changes model to empty DepthLine for creating new line
    new_button = Button('New Line')

    # updates the data arrays for the selected line.  Apply does not do this
    update_arrays_button = Button('Update Data')

    # applys settings to  DepthLine updating object and updating survey line
    apply_button = Button('Apply')

    # applys settings each survey line in selected lines
    apply_to_group = Button('Apply to Group')

    # create local traits so that these options can be dynamically changed
    source_name = Str
    source_names = Property(depends_on=['model.source'])

    # flag allows line creation/edit to continue in apply method
    no_problem = Bool(False)

    # determines whether to show the list of selected groups and lines
    show_selected = Bool(False)

    # list of selected groups and lines by name str for information only
    selected = Property(List, depends_on=['current_survey_line_group',
                                    'selected_survey_lines'])

    # currently selected group
    current_survey_line_group = Supports(ISurveyLineGroup)

    # Set of selected survey lines (including groups) to apply algorithm to
    selected_survey_lines = List(Supports(ISurveyLine))

    # dict of algorithms
    algorithms = Dict

    #==========================================================================
    # Define Views
    #==========================================================================

    traits_view = View(
        'survey_line_name',
        HGroup(
            Item('show_selected', label='Selected(show)'),
            UItem('selected',
                  editor=ListEditor(style='readonly'),
                  style='readonly',
                  visible_when='show_selected')
                   ),
        Item('selected_depth_line_name', label='View Depth Line',
             editor=EnumEditor(name='depth_lines')),
        Item('_'),
        VGroup(Item('object.model.survey_line_name', style='readonly'),
               Item('object.model.name'),
               Item('object.model.line_type'),
               Item('object.model.source'),
               Item('source_name',
                    editor=EnumEditor(name='source_names')),
               Item('args',
                    editor=TextEditor(auto_set=False, enter_set=False),
                    tooltip=ARG_TOOLTIP,
                    visible_when='object.model.source=="algorithm"'
                    ),
               Item('index_array_size', style='readonly'),
               Item('depth_array_size', style='readonly'),
               Item('object.model.edited', style='readonly'),
               Item('object.model.color'),
               Item('object.model.notes',
                    editor=TextEditor(auto_set=False, enter_set=False),
                    style='custom',
                    height=75, resizable=True
                    ),
               Item('object.model.lock'),
               ),
        HGroup(UItem('new_button'),
               UItem('update_arrays_button',
                     tooltip=UPDATE_ARRAYS_TOOLTIP),
               UItem('apply_button',
                     tooltip=APPLY_TOOLTIP),
               UItem('apply_to_group',
                     tooltip=APPLY_TOOLTIP)
               ),
        height=500,
        resizable=True,
    )

    #==========================================================================
    # Defaults
    #==========================================================================

    def _selected_depth_line_name_default(self):
        ''' provide initial value for selected depth line in view'''
        return 'none'

    #==========================================================================
    # Notifications or Callbacks
    #==========================================================================
    def update_plot(self):
        self.data_session.depth_lines_updated = True

    @on_trait_change('new_button')
    def load_new_blank_line(self):
        ''' prepare for creation of new line
        if "none" is already selected, change depth line as if view_depth_line
        was "changed" to "none" (call change depth line with "none"). Otherwise
        change selected line to none and listener will handle it'''
        self.no_problem = True
        if self.selected_depth_line_name == 'none':
            self.change_depth_line(new='none')
        else:
            self.selected_depth_line_name = 'none'

    def depth_line_name_new(self, proposed_line, data_session=None):
        '''check that name is not in survey line depth lines already.
        Allow same name for PRE and POST lists since these are separate
        '''
        if data_session is None:
            data_session = self.data_session
        p = proposed_line
        # new names should begin and end with printable characters.
        p.name = p.name.strip()
        if p.line_type == 'current surface':
            used = p.name in data_session.lake_depths.keys()
        elif p.line_type == 'pre-impoundment surface':
            used = p.name in data_session.preimpoundment_depths.keys()
        else:
            self.log_problem('problem checking depth_line_name_new')
            used = True
        if used:
            s = 'name already used. Unlock to edit existing line'
            self.log_problem(s)
            self.model.lock = True
        return not used

    @on_trait_change('update_arrays_button')
    def update_arrays(self, new):
        ''' apply chosen method to fill line arrays
        '''
        logger.info('applying arrays update {}'.format(self.no_problem))
        model = self.model
        if model.lock:
            self.log_problem('locked so cannot change/create anything')

        # if line is 'none' then this is a new line --'added line'--
        # not a changed line. check name is new
        if self.selected_depth_line_name == 'none':
            self.depth_line_name_new(model)

        if self.no_problem:
            logger.info('no problem in update. try update')
            # name valid.  Try to update data.
            if model.source == 'algorithm':
                alg_name = model.source_name
                args = model.args
                logger.info('applying algorithm : {}'.format(alg_name))
                self.make_from_algorithm(alg_name, args)

            elif model.source == 'previous depth line':
                line_name = model.source_name
                self.make_from_depth_line(line_name)

            else:
                # source is sdi line.  create only from sdi data
                s = 'source "sdi" only available at survey load'
                self.log_problem(s)

    @on_trait_change('apply_button')
    def apply(self, new):
        ''' save current setting and data to current line'''
        model = self.model
        no_depth_array = self.depth_array_size == 0
        no_index_array = self.index_array_size == 0
        depth_notequal_index = self.depth_array_size != self.index_array_size
        if no_depth_array or no_index_array or depth_notequal_index:
            self.no_problem = False
            s = 'data arrays sizes are 0 or not equal'
            self.log_problem(s)
        if self.model.name.strip() == '':
            self.no_problem = False
            s = 'depth line has no printable name'
            self.log_problem(s)
        if self.model.name != self.selected_depth_line_name:
            self.depth_line_name_new(model)
        if model.lock:
            self.log_problem('locked so cannot change/create anything')
        # add to the survey line's appropriate dictionary
        if self.no_problem:
            logger.info('saving new line')
            ds = self.data_session
            if model.line_type == 'current surface':
                ds.lake_depths[self.model.name] = model
                ds.final_lake_depth = self.model.name
                key = 'POST_' + model.name
            else:
                ds.preimpoundment_depths[self.model.name] = model
                ds.final_preimpoundment_depth = self.model.name
                key = 'PRE_' + model.name
                       
            # set form to new line
            self.selected_depth_line_name = key
            self.update_plot()
        else:
            s = '''Could not make new line.
            Did you update Data?
            Check log for details'''
            self.log_problem(s)

    def check_name_and_arrays(self, depth_line=None):
        if depth_line is None:
            depth_line = self.model
        d_array_size = self._array_size(depth_line.depth_array)
        i_array_size = self._array_size(depth_line.index_array)
        no_depth_array = d_array_size == 0
        no_index_array = i_array_size == 0
        depth_notequal_index = d_array_size != i_array_size
        name = self.survey_line_name
        if no_depth_array or no_index_array or depth_notequal_index:
            self.no_problem = False
            s = 'data arrays sizes are 0 or not equal for {}'.format(name)
            self.log_problem(s)
        if self.model.name.strip() == '':
            self.no_problem = False
            s = 'depth line has no printable name'
            self.log_problem(s)

    @on_trait_change('apply_to_group')
    def apply_to_selected(self, new):
        ''' Apply current settings to all selected survey lines

        the will step through selected lines list and
        - check that valid algorithm selected
        - check if depth line exists (overwrite?)
        - check if line is approved (apply?)
        - check if line is bad
        - create line with name and algorithm, args color etc.
        - apply data and apply to make line
        - set as final (?)
        '''
        # save current model to duplicate
        model = self.model
        # list of selected lines
        selected = self.selected_survey_lines
        # check that algorithm is selected and valid
        not_alg = self.model.source != 'algorithm'
        alg_choices = self.algorithms.keys()
        good_alg_name = self.model.source_name in alg_choices
        if not_alg or not good_alg_name:
            self.no_problem = False
            self.log_problem('must select valid algorithm')
        else:
            self.no_problem = True

        # apply to each survey line
        if self.no_problem:
            # log parameters
            lines_str = '\n'.join([line.name for line in selected])
            s = '''Creating depth line for the following surveylines:
            {lines}
            with the following parameters:
            name = {name}
            algorithm = {algorithm}
            args = {args}
            color = {color}
            '''.format(lines=lines_str,
                   name=self.model.name,
                   algorithm=self.source_name,
                   args=self.model.args,
                   color=self.model.color)
            logger.info(s)
            for line in self.selected_survey_lines:
                if line.trace_num.size == 0:
                    # need to load line
                    line.load_data(self.hdf5_file)
                    
                self.model = deepcopy(model)
                self.model.survey_line_name = line.name
                alg_name = model.source_name
                args = model.args
                logger.info('applying algorithm : {}'.format(alg_name))
                self.make_from_algorithm(alg_name, args, survey_line=line)
                self.check_name_and_arrays(self.model)
                if self.no_problem:
                    lname = line.name
                    s = 'saving new depth line to surveyline {}'.format(lname)
                    logger.info(s)
                    print 'saving', self.model, line.name
                    if model.line_type == 'current surface':
                        line.lake_depths[self.model.name] = self.model
                        line.final_lake_depth = self.model.name
                    else:
                        line.preimpoundment_depths[self.model.name] = self.model
                        print line.preimpoundment_depths.keys()
                        line.final_preimpoundment_depth = self.model.name
                    
        self.model = model

    @on_trait_change('selected_depth_line_name')
    def change_depth_line(self, new):
        ''' selected line has changed so use the selection to change the
        current model to selected or create new one if none'''
        if new != 'none':
            # Existing line: edit copy of line until apply button clicked
            new_line = self.data_session.depth_dict[new]
            selected_line = deepcopy(new_line)
        else:
            selected_line = self.create_new_line()
        self.model = selected_line
        self.source_name = selected_line.source_name

    @on_trait_change('source_name')
    def _update_source_name(self):
        self.model.source_name = self.source_name

    #==========================================================================
    # Helper functions
    #==========================================================================
    def message(self, msg='my message'):
        dialog = MsgView(msg=msg)
        dialog.configure_traits()

    def log_problem(self, msg):
        ''' if there is a problem with any part of creating/updating a line,
        log it and notify user and set no_problem flag false'''
        self.no_problem = False
        logger.error(msg)
        self.message(msg)

    def make_from_algorithm(self, alg_name, args, model=None, survey_line=None):
        if model is None:
            model = self.model
        if survey_line is None:
            survey_line = self.data_session.survey_line
        algorithm = self.data_session.algorithms[alg_name]()
        trace_array, depth_array = algorithm.process_line(survey_line,
                                                          **args)
        model.index_array = np.asarray(trace_array, dtype=np.int32) - 1
        model.depth_array = np.asarray(depth_array, dtype=np.float32)
        return model

    def make_from_depth_line(self, line_name):
        source_line = self.data_session.depth_dict[line_name]
        self.model.index_array = source_line.index_array
        self.model.depth_array = source_line.depth_array

    def create_new_line(self):
        ''' fill in some default value and return new depth line object'''
        new_dline = DepthLine(
            survey_line_name=self.survey_line_name,
            name='Type New Name',
            line_type='pre-impoundment surface',
            source='algorithm',
            edited=False,
            lock=False
            )
        logger.info('creating new depthline template')
        return new_dline

    def _array_size(self, array=None):
        if array is not None:
            size = len(array)
        else:
            size = 0
        return size
    
    #==========================================================================
    # Get/Set methods
    #==========================================================================
    def _get_source_names(self):
        source = self.model.source
        if source == 'algorithm':
            names = self.data_session.algorithms.keys()
        elif source == 'previous depth line':
            names = self.data_session.depth_dict.keys()
        else:
            # if source is sdi the source name is just the file it came from
            names = [self.model.source_name]
        return names

    def _get_survey_line_name(self):
        if self.data_session:
            name = self.data_session.survey_line.name
        else:
            name = 'No Survey Line Selected'
        return name

    def _get_depth_lines(self):
        # get list of names of depthlines for the UI
        if self.data_session:
            lines = ['none'] + self.data_session.depth_dict.keys()
        else:
            lines = []
        return lines

    def _get_index_array_size(self):
        a = self.model.index_array
        if a is not None:
            size = len(a)
        else:
            size = 0
        return size

    def _get_depth_array_size(self):
        a = self.model.depth_array
        if a is not None:
            size = len(a)
        else:
            size = 0
        return size

    
    def _get_args(self):
        d = self.model.args
        s = ','.join(['{}={}'.format(k, v) for k, v in d.items()])
        return s

    def _set_args(self, args):
        ''' This is currently not very safe.  Probably better and easier just
        to pass a string that each algorithm will parse appropriately'''
        s = 'dict({})'.format(args)
        d = eval('dict({})'.format(args))
        mod_args = self.model.args
        if isinstance(d, dict):
            if mod_args != d:
                self.model.args = d
        else:
            s = '''Cannot make dictionary out of these arguments,
            Please check the format -- x=1, key=True, ...'''
            self.log_problem(s)
            if mod_args != {}:
                self.model.args = {}

    def _get_selected(self):
        '''make list of selected lines with selected group on top and all lines
        '''
        group_string = 'No Group Selected'
        all_lines = []
        if self.current_survey_line_group:
            group_name = self.current_survey_line_group.name
            group_string = 'GROUP: ' + group_name
        if self.selected_survey_lines:
            all_lines = [line.name for line in self.selected_survey_lines]
            num_lines = len(all_lines)
        else:
            num_lines = 0
        return [group_string] + ['LINES: {}'.format(num_lines)] + all_lines
