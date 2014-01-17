#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import DelegatesTo, Event, List, Str, Supports, on_trait_change
from traitsui.api import View, Item, TreeEditor, TreeNode
from pyface.tasks.api import TraitsDockPane

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine
from ...model.i_survey_line_group import ISurveyLineGroup
from ...util.command_traits import UndoingDelegate


survey_line_tree = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[ISurvey],
            label='name',
            children='',
            rename_me=True,
            delete_me=False,
        ),
        TreeNode(
            node_for=[ISurvey],
            label='=Groups',
            children='survey_line_groups',
        ),
        TreeNode(
            node_for=[ISurvey],
            label='=All Lines',
            children='survey_lines',
            copy=True,
            delete=False,
            delete_me=False,
            rename=True,
            rename_me=False,
        ),
        TreeNode(
            node_for=[ISurveyLineGroup],
            label='name',
            children='survey_lines',
        ),
        TreeNode(
            node_for=[ISurveyLine],
            label='name',
            children='',
        ),
    ],
    selection_mode='extended',
    show_icons=False,
    editable=False,
    hide_root=False,
    selected='selection',
    activated='activated',
)


class SurveyDataPane(TraitsDockPane):
    """ The dock pane holding the data view of the survey """

    id = 'hydropick.survey_data'
    name = 'Survey'

    #: reference to the task's undo manager
    undo_manager = DelegatesTo('task')

    #: proxy for the task's current survey line
    current_survey_line = DelegatesTo('task')

    #: proxy for the task's current survey line
    current_survey_line_group = DelegatesTo('task')

    #: reference to the task's selected survey lines
    selected_survey_lines = DelegatesTo('task')

    #: reference to the survey lines
    survey = Supports(ISurvey)

    #: proxy for the survey's name
    survey_name = UndoingDelegate('survey', 'name', 'undo_manager', trait=Str,
                                   name='Survey Name', mergeable=True)

    #: proxy for the survey's comments field
    survey_comments = UndoingDelegate('survey', 'comments', 'undo_manager',
                                      trait=Str, name='Survey Comments',
                                      mergeable=True)

    #: the currently selected items in the view
    selection = List

    #: the item which has just been activated by double-clicking
    activated = Event

    def _selected_survey_lines_changed(self):
        self.selection = self.selected_survey_lines

    @on_trait_change('selection,selection_items')
    def _selection_updated(self):
        selection = self.selection
        if all(isinstance(item, ISurveyLine) for item in self.selection):
            self.selected_survey_lines = selection
        selected_lines = set()
        for item in selection:
            if isinstance(item, ISurveyLine):
                selected_lines.add(item)
            elif isinstance(item, (ISurveyLineGroup, ISurvey)):
                selected_lines |= set(item.survey_lines)
        if len(selection) == 1 and isinstance(selection[0], ISurveyLineGroup):
            self.current_survey_line_group = selection[0]
        self.selected_survey_lines = list(sorted(selected_lines))

    def _activated_changed(self, item):
        print 'activated', item
        if isinstance(item, ISurveyLine):
            self.current_survey_line = item
        elif isinstance(item, ISurveyLineGroup):
            self.current_survey_line_group = item
            self.selected_survey_lines = item.survey_lines

    view = View(
        Item('survey', editor=survey_line_tree, show_label=False),
    )
