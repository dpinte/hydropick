#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import DelegatesTo, Str, Supports
from traitsui.api import View, Group, Item, TreeEditor, TreeNode
from pyface.tasks.api import TraitsDockPane

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine
from ...model.i_survey_line_group import ISurveyLineGroup
from ...util.command_traits import UndoingDelegate

survey_line_tree = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[ISurvey],
            label='=Groups',
            children='survey_line_groups',
        ),
        TreeNode(
            node_for=[ISurvey],
            label='=All Lines',
            children='survey_lines',
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
