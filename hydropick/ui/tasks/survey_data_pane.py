#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import DelegatesTo, Supports, register_factory, adapt
from traitsui.api import View, Group, Item, TreeEditor, ITreeNode, ITreeNodeAdapter
from pyface.tasks.api import TraitsDockPane

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine
from ...model.i_survey_line_group import ISurveyLineGroup

class ISurveyTreeNodeAdapter(ITreeNodeAdapter):
    """ Adapter for ISurvey objects to ITreeNodes in the UI """

    def allows_children(self):
        return True

    def has_children(self):
        return True

    def get_children(self):
        children = self.adaptee.survey_line_groups + self.adaptee.survey_lines
        return children

    def get_label(self):
        return self.adaptee.name

class ISurveyLineGroupTreeNodeAdapter(ITreeNodeAdapter):

    def allows_children(self):
        return True

    def has_children(self):
        children = self.adaptee.survey_lines
        return len(children) > 0

    def get_children(self):
        children = self.adaptee.survey_lines
        return children

    def get_label(self):
        return self.adaptee.name

class ISurveyLineTreeNodeAdapter(ITreeNodeAdapter):

    def allows_children(self):
        return False

    def get_label(self):
        return self.adaptee.name

def register_adapters():
    register_factory(ISurveyTreeNodeAdapter, ISurvey, ITreeNode)
    register_factory(ISurveyLineTreeNodeAdapter, ISurveyLine, ITreeNode)
    register_factory(ISurveyLineGroupTreeNodeAdapter, ISurveyLineGroup, ITreeNode)

register_adapters()

survey_line_tree = TreeEditor(
    selection_mode='extended',
    show_icons=False,
    editable=False,
    hide_root=True,
    selected='selected_survey_lines',
    activated='current_survey_line',
)


class SurveyDataPane(TraitsDockPane):
    """ The dock pane holding the data view of the survey """

    id = 'hydropick.survey_data'
    name = 'Survey'

    undo_manager = DelegatesTo('task')

    survey = Supports(ISurvey)

    current_survey_line = DelegatesTo('task')

    selected_survey_lines = DelegatesTo('task')

    view = View(
        Item('name'),
        Group(
            Item('survey', editor=survey_line_tree, show_label=False),
        ),
        Group(
            Item('object.survey.comments', style='custom'),
            label='Comments',
            show_labels=False,
        ),
    )
