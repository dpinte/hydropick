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
from traits.api import (Instance, Str, Dict, Property, HasTraits, Enum, Int,
                        on_trait_change, Button, DelegatesTo)
from traitsui.api import (View, VGroup, HGroup, Item, EnumEditor, TextEditor)

# Local imports
from ..model.depth_line import DepthLine
from .survey_data_session import SurveyDataSession
from .survey_views import MsgView

logger = logging.getLogger(__name__)

ARG_TOOLTIP = 'comma separated keyword args -- x=1,all=True,s="Tom"'


#class DepthLineView(ModelView):
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
    survey_line_name = Property(depends_on=['data_session',
                                            'data_session.depth_lines_updated']
                                )

    # list of available depth lines extracted from survey line
    depth_lines = Property(depends_on='data_session')

    # name of depth_line to view chosen from pulldown of all available lines.
    selected_depth_line_name = Str

    # current depth line object
    model = Instance(DepthLine)

    args = Property(Str, depends_on=['model.args', 'model'])
    index_array_size = Property(Int, depends_on=['model.index_array, model'])
    depth_array_size = Property(Int, depends_on=['model.depth_array, model'])

    # changes model to empty DepthLine for creating new line
    new_button = Button('New Line')

    # applys settings to  DepthLine updating object and updating survey line
    apply_button = Button('Apply')

    source_name = Str
    source_names = Property(depends_on=['model.source, model'])
    #==========================================================================
    # Define Views
    #==========================================================================

    traits_view = View(
        'survey_line_name',
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
        HGroup('new_button', 'apply_button'),
        height=500,
        resizable=True,
    )

    #==========================================================================
    # Defaults
    #==========================================================================

    def _selected_depth_line_name_default(self):
        ''' Create initial plot container'''
        return 'none'

    #==========================================================================
    # Notifications or Callbacks
    #==========================================================================
    def update_plot(self):
        self.data_session.depth_lines_updated = True

    @on_trait_change('new_button')
    def load_new_blank_line(self):
        if self.selected_depth_line_name == 'none':
            self.change_depth_line(new='none')
        else:
            self.selected_depth_line_name = 'none'

    def create_new_line(self):
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

    @on_trait_change('apply_button')
    def apply(self, new):
        ''' apply appropriate method to fill line'''
        model = self.model
        if model.lock:
            'locked so cannot change anything'
            return
        success = True
        # if line is none then this is a new line 'added line'
        # not a changed line
        if self.selected_depth_line_name == 'none':
            if model.source == 'algorithm':
                alg_name = model.source_name
                args = model.args
                self.make_from_algorithm(alg_name, args)
                logger.info('applying algorithm : {}'.format(alg_name))

            elif model.source == 'previous depth line':
                line_name = model.source_name
                self.make_from_depth_line(line_name)

            else:
                # source is sdi line.  create only from sdi data
                logger.error('sdi source only available at survey load')
                return

            # if selected line not none then we will apply changes and
            # save to saved lines with same name (changed line)

        # add to survey line depth line dictionary
        if success:
            print 'saving line'
            ds = self.data_session
            if model.line_type == 'current surface':
                ds.lake_depths[self.model.name] = model
                key = 'POST_' + model.name
            else:
                ds.preimpoundment_depths[self.model.name] = model
                key = 'PRE_' + model.name
            # set form to new line
            self._get_survey_line_name()
            self.selected_depth_line_name = key
            self.update_plot()
        else:
            return

    @on_trait_change('selected_depth_line_name')
    def change_depth_line(self, new):
        if new != 'none':
            new_line = self.data_session.depth_dict[new]
            selected_line = deepcopy(new_line)
        else:
            selected_line = self.create_new_line()
        self.model = selected_line
        self.source_name = selected_line.source_name
        print 'changed lines',self.model,self.model.name, selected_line.source_name, self.source_name

    @on_trait_change('source_name')
    def _update_source_name(self):
        self.model.source_name = self.source_name
        print 'updated source name',self.model.source_name

    #==========================================================================
    # Helper functions
    #==========================================================================
    def message(self, msg='my message'):
        dialog = MsgView(msg=msg)
        dialog.configure_traits()

    def make_from_algorithm(self, alg_name, args):
        algorithm = self.data_session.algorithms[alg_name]()
        survey_line = self.data_session.survey_line
        print 'args are', args, type(args)

        trace_array, depth_array = algorithm.process_line(survey_line,
                                                          **args)
        print trace_array, depth_array, algorithm
        self.model.index_array = np.asarray(trace_array, dtype=np.int32) - 1
        self.model.depth_array = np.asarray(depth_array, dtype=np.float32)

    def make_from_depth_line(self, line_name):
        source_line = self.data_session.depth_dict[line_name]
        self.model.index_array = source_line.index_array
        self.model.depth_array = source_line.depth_array

    #==========================================================================
    # Get/Set methods
    #==========================================================================
    def _get_source_names(self):
        source = self.model.source
        print 'new source is', source
        print source, source == 'previous depth line'
        if source == 'algorithm':
            names = self.data_session.algorithms.keys()
            print self.data_session.algorithms
        elif source == 'previous depth line':
            print 'prev'
            print self.data_session.depth_dict.keys()
            names = self.data_session.depth_dict.keys()
            print self.data_session.depth_dict.keys()
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
        # get lisyyt of names of depthlines for the UI
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
        print 'args',d,s
        return s

    def _set_args(self, args):
        print 'set args', args
        s='dict({})'.format(args)
        d = eval('dict({})'.format(args))
        print d
        mod_args = self.model.args
        if isinstance(d, dict):
            if mod_args != d:
                self.model.args = d
        else:
            s = '''Cannot make dictionary out of these arguments,
            Please check the format -- x=1, key=True, ...'''
            self.message(s)
            if mod_args != {}:
                self.model.args = {}
