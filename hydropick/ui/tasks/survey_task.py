#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Supports, List
from pyface.action.api import Action
from pyface.tasks.api import Task, TaskLayout, PaneItem
from pyface.tasks.action.api import DockPaneToggleGroup, SMenuBar, SMenu, \
    SGroup, TaskAction
from apptools.undo.i_undo_manager import IUndoManager
from apptools.undo.i_command_stack import ICommandStack

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine
from ...model.i_survey_line_group import ISurveyLineGroup

class SurveyTask(Task):
    """ A task for viewing and editing hydrological survey data """

    #### Task interface #######################################################

    id = 'hydropick.survey_task'
    name = 'Survey Editor'


    #### SurveyTask interface #######################################################

    # XXX perhaps bundle the survey specific things into a survey manager object?

    #: the survey object that we are viewing
    survey = Supports(ISurvey)

    #: the currently active survey line group
    current_survey_line_group = Supports(ISurveyLineGroup)

    #: the currently active survey line that we are viewing
    current_survey_line = Supports(ISurveyLine)

    #: the selected survey lines
    selected_survey_lines = List(Supports(ISurveyLine))

    #: the object that manages Undo/Redo stacks
    undo_manager = Supports(IUndoManager)

    #: the object that holds the Task's commands
    command_stack = Supports(ICommandStack)

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def _default_layout_default(self):
        return TaskLayout(left=PaneItem('hydropick.survey_map'))

    def _menu_bar_default(self):
        from apptools.undo.action.api import UndoAction, RedoAction
        menu_bar = SMenuBar(
            SMenu(
                SGroup(
                    TaskAction(name="Open", method='on_open', accelerator='Ctrl+O'),
                    id='Open', name='Open'
                ),
                SGroup(
                    TaskAction(name="Save", method='on_save', accelerator='Ctrl+S'),
                    TaskAction(name="Save As...", method='on_save_as', accelerator='Ctrl+Shift+S'),
                    id='Save', name='Save'
                ),
                id='File', name="&File",
            ),
            SMenu(
                SGroup(
                    UndoAction(undo_manager=self.undo_manager),
                    RedoAction(undo_manager=self.undo_manager),
                    id='UndoGroup', name="Undo Group",
                ),
                SGroup(
                    Action(name='Cut', accelerator='Ctrl+X'),
                    Action(name='Copy', accelerator='Ctrl+C'),
                    Action(name='Paste', accelerator='Ctrl+V'),
                    id='CopyGroup', name="Copy Group",
                ),
                SGroup(
                    TaskAction(name='New Group', method='on_new_group', accelerator='Ctrl+N'),
                    TaskAction(name='Delete Group', method='on_delete_group', accelerator='Ctrl+Delete'),
                    id='LineGroupGroup', name="Line Group Group",
                ),
                id='Edit', name="&Edit",
            ),
            SMenu(
                SGroup(
                    TaskAction(name='Next Line', method='on_next_line',
                                enabled_name='selected_survey_lines', accelerator='Ctrl+Right'),
                    TaskAction(name='Previous Line', method='on_previous_line',
                                enabled_name='selected_survey_lines', accelerator='Ctrl+Left'),
                    id='LineGroup', name='Line Group',
                ),
                DockPaneToggleGroup(),
                id='View', name="&View",
            ),
        )
        return menu_bar

    def activated(self):
        """ Overriden to set the window's title.
        """
        name = self.survey.name
        self.window.title = name if name else 'Untitled'

    def create_central_pane(self):
        """ Create the central pane: the editor pane.
        """
        from .survey_line_pane import SurveyLinePane
        pane = SurveyLinePane()
        # listen for changes to the current survey line
        self.on_trait_change(lambda new: setattr(pane, 'survey_line', new),
                            'current_survey_line')
        return pane

    def create_dock_panes(self):
        """ Create the map pane and hook up listeners
        """
        from .survey_map_pane import SurveyMapPane
        map = SurveyMapPane(survey=self.survey)
        return [map]

    ###########################################################################
    # 'SurveyTask' interface.
    ###########################################################################

    def on_open(self):
        """ Opens a hydrological survey file """
        pass

    def on_save(self):
        """ Saves a hydrological survey file """
        pass

    def on_save_as(self):
        """ Saves a hydrological survey file in a different location """
        pass

    def on_next_line(self):
        """ Move to the next selected line """
        pass

    def on_previous_line(self):
        """ Move to the previous selected line """
        pass

    def on_new_group(self):
        from ..model.survey_line_group import SurveyLineGroup
        from ..utils.commands import CallableCommand

        group = SurveyLineGroup(lines=self.selected_lines)
        command = CallableCommand(
            do_callable=self.survey.survey_line_groups.append,
            undo_callable=self.survey.survey_line_groups.remove,
            args=((group,), {})
        )
        self.undo_manager.active_stack.push(command)

    def _command_stack_default(self):
        """ Return the default undo manager """
        from apptools.undo.api import CommandStack
        command_stack = CommandStack()
        return command_stack

    def _undo_manager_default(self):
        """ Return the default undo manager """
        from apptools.undo.api import UndoManager
        undo_manager = UndoManager(active_stack=self.command_stack)
        return undo_manager
