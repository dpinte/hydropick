#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import logging

from chaco.api import Plot
from traits.api import (DelegatesTo, Instance, on_trait_change, Property,
                        Supports, Bool)
from traitsui.api import View, Item, ModelView
from enable.component_editor import ComponentEditor
from pyface.tasks.api import TraitsDockPane

from hydropick.ui.survey_depth_line_view import DepthLineView
from hydropick.model.i_survey_line import ISurveyLine
from hydropick.model.depth_line import DepthLine

logger = logging.getLogger(__name__)

class SurveyDepthPane(TraitsDockPane):
    """ The dock pane holding the map view of the survey """

    id = 'hydropick.survey_depth_line'
    name = "Depth Line"

    survey = DelegatesTo('task')

    #: proxy for the task's current survey line
    current_survey_line = DelegatesTo('task')

    #: proxy for the task's current survey line
    current_survey_line_group = DelegatesTo('task')

    #: reference to the task's selected survey lines
    selected_survey_lines = DelegatesTo('task')

    current_data_session = DelegatesTo('task')

    depth_line_view = Instance(DepthLineView)

    depth_line = Instance(DepthLine)

    #: proxy for the editor's current depth line
    selected_depth_line_name = DelegatesTo('task')

    # dict of algorithms
    algorithms = DelegatesTo('task')
    
    #hdf5_file = Property(depends_on='survey')

    show_view = Bool(False)

    def _depth_line_view_default(self):
        return None

    def _selected_depth_line_name_changed(self):
        print 'dlp-selectd_dln_chng'
        logger.info('dlp-selectd_dln_chng')
        name = self.selected_depth_line_name
        d = self.current_data_session.depth_dict[self.selected_depth_line_name]
        self.depth_line_view.model = d
        self.depth_line_view.selected_depth_line_name = name

    @on_trait_change('selected_survey_lines')
    def update_depth_view_survey_lines(self):
        self._update_depth_view_survey_lines()
        
    def _update_depth_view_survey_lines(self, view=None):
        if view is None:
            view = self.depth_line_view
        if view:
            view.selected_survey_lines = self.selected_survey_lines
            if self.current_survey_line_group:
                group = self.current_survey_line_group
                view.current_survey_line_group = group

    @on_trait_change('current_survey_line')
    def log_line_change(self):
        name = self.current_survey_line
        if name:
            name = name.name
        logger.info('current survey line now {}'.format(name))
        
    def _get_hdf5_file(self):
        return self.survey.hdf5_file
    
    @on_trait_change('current_data_session')
    def _set_depth_line_view(self):
        name = self.current_data_session
        if self.current_data_session:
            self.depth_line_view = self._get_depth_line_view()
            name = self.current_data_session.survey_line.name
        logger.info('data session changed: {}'.format(name))
        
    def _get_depth_line_view(self):
        data = self.current_data_session
        sanity_check = data.survey_line is self.current_survey_line
        if data and sanity_check:
            view = DepthLineView(model=DepthLine(),
                                 selected_depth_line_name='none',
                                 data_session=self.current_data_session,
                                 algorithms=self.algorithms,
                                 hdf5_file=self.survey.hdf5_file
                                 )
            if self.selected_survey_lines:
                self._update_depth_view_survey_lines(view=view)
            self.show_view = True
        else:
            view = None
            self.show_view = False
        return view

    view = View(
        Item('depth_line_view',
             style='custom',
             visible_when='show_view',
             show_label=False
             ),
        kind='nonmodal'
        )
