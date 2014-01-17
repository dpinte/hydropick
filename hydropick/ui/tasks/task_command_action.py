#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from __future__ import absolute_import

from traits.api import Instance, Property, Str, cached_property
from pyface.tasks.api import TaskPane, Editor
from pyface.tasks.action.api import CentralPaneAction, DockPaneAction, \
    EditorAction, TaskAction, TaskWindowAction
from pyface.tasks.action.listening_action import ListeningAction
from apptools.undo.action.api import CommandAction


class ListeningCommandAction(CommandAction, ListeningAction):
    """ A CommandAction which listens for data and gets its command from an object

    If the `method` attribute is set, it should refer to a method that returns
    an appropriate `apptools.undo.command.Command` instance, otherwise the
    action will use the `command` attribute to generate the command.

    """

    #### 'ListeningCommandAction' interface ###################################

    #: the (extended) name of the attribute that determines the data on which
    #: the command operates. By default, the data is the object.
    data_name = Str

    #: the (extended) name of the attribute that determines the command stack on
    #: which the command is pushed. If this is empty then it assumed that the
    #: command stack is being directly supplied to the Action.
    command_stack_name = Str

    ###########################################################################
    # 'Action' interface.
    ###########################################################################

    def destroy(self):
        """ Called when the action is no longer required.

        Remove all the listeners.

        """
        if self.object:
            for kind in self._listened_attributes:
                method = getattr(self, '_%s_update' % kind)
                name = getattr(self, '%s_name' % kind)
                self.object.on_trait_change(method, name, remove=True)

    def perform(self, event=None):
        """ Call the appropriate function.
        """
        if self.method != '':
            method = self._get_attr(self.object, self.method)
            if method:
                command = method()
                self.command_stack.push(command)
        else:
            super(ListeningCommandAction, self).perform(event)

    ###########################################################################
    # Protected interface.
    ###########################################################################

    _listened_attributes = ('enabled', 'visible', 'data', 'command_stack')

    #### Trait change handlers ################################################

    def _object_changed(self, old, new):
        for kind in self._listened_attributes:
            method = getattr(self, '_%s_update' % kind)
            name = getattr(self, '%s_name' % kind)
            if name:
                if old:
                    old.on_trait_change(method, name, remove=True)
                if new:
                    new.on_trait_change(method, name)
            method()

    def _data_name_changed(self, old, new):
        obj = self.object
        if obj is not None:
            if old:
                obj.on_trait_change(self._data_update, old, remove=True)
            if new:
                obj.on_trait_change(self._data_update, new)
        self._data_update()

    def _data_update(self):
        if self.data_name:
            if self.object:
                self.data = self._get_attr(self.object, self.data_name, None)
            else:
                self.data = None
        else:
            self.data = self.object

    def _command_stack_name_changed(self, old, new):
        obj = self.object
        if obj is not None:
            if old:
                obj.on_trait_change(self._command_stack_update, old, remove=True)
            if new:
                obj.on_trait_change(self._command_stack_update, new)
        self._command_stack_update()

    def _command_stack_update(self):
        if self.command_stack_name:
            if self.object:
                self.command_stack = self._get_attr(self.object,
                                                    self.command_stack_name,
                                                    None)
            else:
                self.command_stack = None


class TaskCommandAction(ListeningCommandAction, TaskAction):
    """ A CommandAction associated with a Task

    If the `method` attribute is set, it should refer to a method that returns
    an appropriate `apptools.undo.command.Command` instance, otherwise the
    action will use the `command` attribute to generate the command.

    """
    #### ListeningAction interface ############################################

    object = Property(depends_on='task')

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _get_object(self):
        return self.task


class TaskWindowCommandAction(ListeningCommandAction, TaskWindowAction):
    """ A CommandAction associated with a TaskWindow

    If the `method` attribute is set, it should refer to a method that returns
    an appropriate `apptools.undo.command.Command` instance, otherwise the
    action will use the `command` attribute to generate the command.

    """

    #### ListeningAction interface ############################################

    object = Property(depends_on='task.window')

    ###########################################################################
    # Protected interface.
    ###########################################################################

    def _get_object(self):
        if self.task:
            return self.task.window
        return None


class CentralPaneCommandAction(ListeningCommandAction, CentralPaneAction):
    """ A CommandAction associated with a CentralPane

    If the `method` attribute is set, it should refer to a method that returns
    an appropriate `apptools.undo.command.Command` instance, otherwise the
    action will use the `command` attribute to generate the command.

    """

    #### ListeningAction interface ############################################

    object = Property(depends_on='central_pane')

    #### CentralPaneAction interface ##########################################

    # The central pane with which the action is associated.
    central_pane = Property(Instance(TaskPane), depends_on='task')

    ###########################################################################
    # Protected interface.
    ###########################################################################

    @cached_property
    def _get_central_pane(self):
        if self.task:
            return self.task.window.get_central_pane(self.task)
        return None

    def _get_object(self):
        return self.central_pane


class DockPaneCommandAction(ListeningCommandAction, DockPaneAction):
    """ A CommandAction associated with a DockPane

    If the `method` attribute is set, it should refer to a method that returns
    an appropriate `apptools.undo.command.Command` instance, otherwise the
    action will use the `command` attribute to generate the command.

    """

    #### ListeningAction interface ############################################

    object = Property(depends_on='dock_pane')

    #### DockPaneAction interface #############################################

    # The dock pane with which the action is associated. Set by the framework.
    dock_pane = Property(Instance(TaskPane), depends_on='task')

    ###########################################################################
    # Protected interface.
    ###########################################################################

    @cached_property
    def _get_dock_pane(self):
        if self.task:
            return self.task.window.get_dock_pane(self.dock_pane_id, self.task)
        return None

    def _get_object(self):
        return self.dock_pane


class EditorCommandAction(ListeningCommandAction, EditorAction):
    """ A CommandAction associated with an Editor

    If the `method` attribute is set, it should refer to a method that returns
    an appropriate `apptools.undo.command.Command` instance, otherwise the
    action will use the `command` attribute to generate the command.

    """
    #### ListeningAction interface ############################################

    object = Property(depends_on='active_editor')

    #### EditorAction interface ###############################################

    # The active editor in the central pane with which the action is associated.
    active_editor = Property(Instance(Editor),
                             depends_on='central_pane.active_editor')

    ###########################################################################
    # Protected interface.
    ###########################################################################

    @cached_property
    def _get_active_editor(self):
        if self.central_pane is not None:
            return self.central_pane.active_editor
        return None

    def _get_object(self):
        return self.active_editor
