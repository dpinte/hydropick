#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import (Bool, Property, Supports, List, on_trait_change, Dict)

from pyface.api import ImageResource
from pyface.tasks.api import Task, TaskLayout, PaneItem, VSplitter
from pyface.tasks.action.api import DockPaneToggleGroup, SMenuBar, SMenu, \
    SGroup, SToolBar, TaskAction, CentralPaneAction
from apptools.undo.i_undo_manager import IUndoManager
from apptools.undo.i_command_stack import ICommandStack

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine
from ...model.i_survey_line_group import ISurveyLineGroup
from ...model import algorithms

from .task_command_action import TaskCommandAction

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

    # traits for managing Action state

    #: whether the undo stack is "clean"
    dirty = Property(Bool, depends_on='command_stack.clean')

    #: whether or not there are selected lines
    have_selected_lines = Property(Bool, depends_on='selected_survey_lines')

    #: whether or not there is a current group
    have_current_group = Property(Bool, depends_on='current_survey_line_group')

    #: the object that manages Undo/Redo stacks
    undo_manager = Supports(IUndoManager)

    #: the object that holds the Task's commands
    command_stack = Supports(ICommandStack)

    #: reference to dictionary of available depth pic algorithms
    #(IAlgorithm Classes)
    algorithms = Dict

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def _default_layout_default(self):
        return TaskLayout(left=VSplitter(PaneItem('hydropick.survey_data'),
                                        PaneItem('hydropick.survey_map')))

    def _menu_bar_default(self):
        from apptools.undo.action.api import UndoAction, RedoAction
        menu_bar = SMenuBar(
            SMenu(
                SGroup(
                    TaskAction(name="Import", method='on_import', accelerator='Ctrl+I'),
                    id='New', name='New'
                ),
                SGroup(
                    TaskAction(name="Open", method='on_open', accelerator='Ctrl+O'),
                    id='Open', name='Open'
                ),
                SGroup(
                    TaskAction(name="Save", method='on_save', accelerator='Ctrl+S', enabled_name='dirty'),
                    TaskAction(name="Save As...", method='on_save_as', accelerator='Ctrl+Shift+S', enabled_name='survey'),
                    id='Save', name='Save'
                ),
                id='File', name="&File",
            ),
            SMenu(
                # XXX can't integrate easily with TraitsUI editors :P
                SGroup(
                    UndoAction(undo_manager=self.undo_manager, accelerator='Ctrl+Z'),
                    RedoAction(undo_manager=self.undo_manager, accelerator='Ctrl+Shift+Z'),
                    id='UndoGroup', name="Undo Group",
                ),
                SGroup(
                    TaskCommandAction(name='New Group', method='on_new_group',
                                      accelerator='Ctrl+Shift+N',
                                      command_stack_name='command_stack'),
                    TaskCommandAction(name='Delete Group',
                                      method='on_delete_group',
                                      accelerator='Ctrl+Delete',
                                      enabled_name='have_current_group',
                                      command_stack_name='command_stack'),
                    id='LineGroupGroup', name="Line Group Group",
                ),
                id='Edit', name="&Edit",
            ),
            SMenu(
                SGroup(
                    TaskAction(name='Next Line',
                               method='on_next_line',
                               enabled_name='survey.survey_lines',
                               accelerator='Ctrl+Right'),
                    TaskCommandAction(name='Previous Line',
                               method='on_previous_line',
                               enabled_name='survey.survey_lines',
                               accelerator='Ctrl+Left'),
                    id='LineGroup', name='Line Group',
                ),
                DockPaneToggleGroup(),
                id='View', name="&View",
            ),
            SMenu(
                SGroup(
                    CentralPaneAction(name='New Depth Line',
                               method='on_new_depth_line',
                               enabled_name='show_view',
                               accelerator='Ctrl+Shift+='),
                    id='ToolGroup', name='Tool Group',
                ),
                id='Tools', name="&Tools",
            ),
        )
        return menu_bar

    def _tool_bars_default(self):
        toolbars = [
            SToolBar(
                TaskAction(name="Import", method='on_import',
                            image=ImageResource('import')),
                TaskAction(name="Open", method='on_open',
                            image=ImageResource('survey')),
                TaskAction(name="Save", method='on_save',
                            enabled_name='dirty',
                            image=ImageResource('save')),
                id='File', name="File", show_tool_names=False, image_size=(24,24)
            ),
            SToolBar(
                TaskCommandAction(name='New Group', method='on_new_group',
                                  command_stack_name='command_stack',
                                  image=ImageResource('new-group')),
                TaskCommandAction(name='Delete Group',
                                  method='on_delete_group',
                                  enabled_name='have_current_group',
                                  command_stack_name='command_stack',
                                  image=ImageResource('delete-group')),
                TaskAction(name='Previous Line',
                           method='on_previous_line',
                           enabled_name='survey.survey_lines',
                           image=ImageResource("arrow-left")),
                TaskAction(name='Next Line',
                           method='on_next_line',
                           enabled_name='survey.survey_lines',
                           image=ImageResource("arrow-right")),
                id='Survey', name="Survey", show_tool_names=False, image_size=(24,24)
            ),
        ]
        return toolbars

    def activated(self):
        """ Overriden to set the window's title.
        """
        self.window.title = self._window_title()

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
        from .survey_data_pane import SurveyDataPane
        from .survey_map_pane import SurveyMapPane

        data = SurveyDataPane(survey=self.survey)
        self.on_trait_change(lambda new: setattr(data, 'survey', new), 'survey')

        map = SurveyMapPane(survey=self.survey)
        self.on_trait_change(lambda new: setattr(map, 'survey', new), 'survey')
        return [data, map]

    def _survey_changed(self):
        from apptools.undo.api import CommandStack
        self.current_survey_line = None
        self.current_survey_line_group = None
        self.selected_survey_lines = []
        # reset undo stack
        self.command_stack = CommandStack(undo_manager=self.undo_manager)
        self.undo_manager.active_stack = self.command_stack

    @on_trait_change('survey.name')
    def update_title(self):
        if self.window and self.window.active_task is self:
            self.window.title = self._window_title()

    @on_trait_change('survey.survey_lines')
    def survey_lines_updated(self):
        if self.current_survey_line not in self.survey.survey_lines:
            self.current_survey_line = None
        self.selected_survey_lines[:] = [line for line in self.selected_survey_lines
                                         if line in self.survey_lines]


    @on_trait_change('survey.survey_line_groups')
    def survey_line_groups_updated(self):
        if self.current_survey_line_group not in self.survey.survey_line_groups:
            self.current_survey_line_group = None

    ###########################################################################
    # 'SurveyTask' interface.
    ###########################################################################

    def on_import(self):
        """ Imports hydrological survey data """
        from pyface.api import DirectoryDialog, OK
        from ...io.import_survey import import_survey

        # ask the user for save if needed
        self._prompt_for_save()

        survey_directory = DirectoryDialog(message="Select survey to import:",
                                            new_directory=False)
        if survey_directory.open() == OK:
            survey = import_survey(survey_directory.path)
            self.survey = survey

    def on_open(self):
        """ Opens a hydrological survey file """
        self._prompt_for_save()
        raise NotImplementedError

    def on_save(self):
        """ Saves a hydrological survey file """
        raise NotImplementedError

    def on_save_as(self):
        """ Saves a hydrological survey file in a different location """
        raise NotImplementedError

    def on_new_group(self):
        """ Adds a new survey line group to a survey """
        from ...model.survey_line_group import SurveyLineGroup
        from ...model.survey_commands import AddSurveyLineGroup

        group = SurveyLineGroup(name='Untitled', survey_lines=self.selected_survey_lines)
        command = AddSurveyLineGroup(data=self.survey, group=group)
        return command

    def on_delete_group(self):
        """ Deletes a survey line group from a survey """
        from ...model.survey_line_group import SurveyLineGroup
        from ...model.survey_commands import DeleteSurveyLineGroup

        group = self.current_survey_line_group
        command = DeleteSurveyLineGroup(data=self.survey, group=group)
        return command

    def on_next_line(self):
        """ Move to the next selected line """
        self.current_survey_line = self._get_next_survey_line()

    def on_previous_line(self):
        """ Move to the previous selected line """
        self.current_survey_line = self._get_previous_survey_line()

    def _get_dirty(self):
        return not self.command_stack.clean

    def _get_have_selected_lines(self):
        return len(self.selected_survey_lines) != 0

    def _get_have_current_group(self):
        return self.current_survey_line_group is not None

    def _command_stack_default(self):
        """ Return the default undo manager """
        from apptools.undo.api import CommandStack
        command_stack = CommandStack()
        return command_stack

    def _undo_manager_default(self):
        """ Return the default undo manager """
        from apptools.undo.api import UndoManager
        undo_manager = UndoManager(active_stack=self.command_stack)
        self.command_stack.undo_manager = undo_manager
        return undo_manager

    def _survey_default(self):
        from ...model.survey import Survey
        return Survey(name='New Survey')

    def _algorithms_default(self):
        name_list = algorithms.ALGORITHM_LIST
        classes = [getattr(algorithms, cls_name) for cls_name in name_list]
        names = [cls().name for cls in classes]
        return dict(zip(names, classes))


    ###########################################################################
    # private interface.
    ###########################################################################

    def _window_title(self):
        """ Get the title of the window """
        name = self.survey.name
        return name if name else 'Untitled'

    def _prompt_for_save(self):
        """ Check if the user wants to save changes """
        from pyface.api import ConfirmationDialog, CANCEL, YES
        if not self.command_stack.clean:
            message = 'The current survey has unsaved changes. ' \
                      'Do you want to save your changes?'
            dialog = ConfirmationDialog(parent=self.window.control,
                                        message=message, cancel=True,
                                        default=CANCEL, title='Save Changes?')
            result = dialog.open()
            if result == CANCEL:
                return False
            elif result == YES:
                if not self._save():
                    return self._prompt_for_save()
        return True

    def _save(self):
        """ Save changes to a survey file """
        raise NotImplementedError

    def _get_next_survey_line(self):
        """ Get the next selected survey line, or the next line if nothing selected """
        survey_lines = self.selected_survey_lines[:]
        previous_survey_line = self.current_survey_line

        # if nothing selected, use all survey lines
        if len(survey_lines) == 0:
            survey_lines = self.survey.survey_lines[:]

        # if still nothing, can't do anything reasonable, but we shouldn't
        # have been called
        if len(survey_lines) == 0:
            return None

        if previous_survey_line in survey_lines:
            index = (survey_lines.index(previous_survey_line)+1) % \
                    len(survey_lines)
            return survey_lines[index]
        else:
            return survey_lines[0]

    def _get_previous_survey_line(self):
        """ Get the previous selected survey line, or the previous line if nothing selected """
        survey_lines = self.selected_survey_lines[:]
        previous_survey_line = self.current_survey_line

        # if nothing selected, use all survey lines
        if len(survey_lines) == 0:
            survey_lines = self.survey.survey_lines[:]

        # if still nothing, can't do anything reasonable, but we shouldn't
        # have been called
        if len(survey_lines) == 0:
            return None

        if previous_survey_line in survey_lines:
            index = (survey_lines.index(previous_survey_line)-1) % \
                    len(survey_lines)
            return survey_lines[index]
        else:
            return survey_lines[-1]
