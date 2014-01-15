#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import DelegatesTo, Str, Supports, register_factory
from traitsui.api import View, Group, Item, TreeEditor, ITreeNode, ITreeNodeAdapter
from pyface.tasks.api import TraitsDockPane

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine
from ...model.i_survey_line_group import ISurveyLineGroup
from ...util.command_traits import UndoingDelegate

class ISurveyTreeNodeAdapter(ITreeNodeAdapter):
    """ Adapter for ISurvey objects to ITreeNodes in the UI """

    def allows_children(self):
        return True

    def has_children(self):
        return True

    def get_children(self):
        children = self.adaptee.survey_line_groups + self.adaptee.survey_lines
        return children

    def when_children_changed(self, listener, remove):
        self.adaptee.on_trait_change(listener, 'survey_line_groups_items',
                                     remove=remove)
        self.adaptee.on_trait_change(listener, 'survey_lines_items',
                                     remove=remove)

    def when_children_replaced(self, listener, remove):
        self.adaptee.on_trait_change(listener, 'survey_line_groups',
                                     remove=remove)
        self.adaptee.on_trait_change(listener, 'survey_lines', remove=remove)

    def get_label(self):
        return self.adaptee.name

class ISurveyLineGroupTreeNodeAdapter(ITreeNodeAdapter):
    """ Adapter for ISurveyLineGroup objects to ITreeNodes in the UI """

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
    """ Adapter for ISurveyLine objects to ITreeNodes in the UI """

    def allows_children(self):
        return False

    def get_label(self):
        return self.adaptee.name

def register_adapters():
    register_factory(ISurveyTreeNodeAdapter, ISurvey, ITreeNode)
    register_factory(ISurveyLineTreeNodeAdapter, ISurveyLine, ITreeNode)
    register_factory(ISurveyLineGroupTreeNodeAdapter, ISurveyLineGroup, ITreeNode)

register_adapters()

# XXX unsure if we need all of the above - may be better to use TreeNodes instead

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

    #: reference to the task's undo manager
    undo_manager = DelegatesTo('task')

    #: proxy for the task's current survey line
    current_survey_line = UndoingDelegate('task', 'current_survey_line',
                                          'undo_manager',
                                          name='Select Survey Line')

    #: reference to the task's selected survey lines
    selected_survey_lines = DelegatesTo('task')

    #: reference to the survey lines
    survey = Supports(ISurvey)

    #: proxy for the survey's name
    survey_name = UndoingDelegate('survey', 'name', 'undo_manager', trait=Str,
                                   name='Survey Name', mergeable=True)

    #: proxy for the survey's comments field
    survey_comments = UndoingDelegate('survey', 'comments', 'undo_manager', trait=Str,
                                      name='Survey Comments', mergeable=True)

    view = View(
        Item('survey_name'),
        Group(
            Item('survey', editor=survey_line_tree, show_label=False),
            label='Survey Lines',
        ),
        Group(
            Item('survey_comments', style='custom'),
            label='Comments',
            show_labels=False,
        ),
    )
