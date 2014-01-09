#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Supports, List
from pyface.action.api import Action
from pyface.tasks.api import Task, TaskLayout
from pyface.tasks.action.api import DockPaneToggleGroup, SMenuBar, SMenu, \
    SGroup, TaskAction
from apptools.undo.i_undo_manager import IUndoManager

from ...model.i_survey import ISurvey
from ...model.i_survey_line import ISurveyLine

class SurveyTask(Task):
    """ A task for viewing and editing hydrological survey data """

    #### Task interface #######################################################

    id = 'hydropick.survey_task'
    name = 'Survey Editor'


    #### SurveyTask interface #######################################################

    # XXX perhaps bundle the survey specific things into a survey manager object?

    #: the survey object that we are viewing
    survey = Supports(ISurvey)

    #: the currently active survey line that we are viewing
    current_survey_line = Supports(ISurveyLine)

    #: the selected survey lines
    selected_survey_lines = List(Supports(ISurveyLine))

    #: the object that manages Undo/Redo stacks
    undo_manager = Supports(IUndoManager)

    ###########################################################################
    # 'Task' interface.
    ###########################################################################

    def _default_layout_default(self):
        return TaskLayout()

    def _menubar_default(self):
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
                    id='UndoGroup', name="Undo Group",
                ),
                id='Edit', name="&Edit",
            ),
            SMenu(
                SGroup(
                    TaskAction(name='Next Line', method='on_next_line'),
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

    def _undo_manager_default(self):
        """ Return the default undo manager """
        from apptools.undo.api import UndoManager
        undo_manager = UndoManager()
        return undo_manager
