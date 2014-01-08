#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#

from __future__ import absolute_import

from unittest import TestCase

from traits.api import HasTraits, Int
from apptools.undo.api import UndoManager, CommandStack

from ..commands import AttributeSetCommand

class TargetClass(HasTraits):

    value = Int


class TestAttributeSetCommand(TestCase):

    def setUp(self):
        self.manager = UndoManager()
        self.stack = CommandStack(undo_manager=self.manager)
        self.manager.active_stack = self.stack
        self.target = TargetClass()

    def test_command_do(self):
        command = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1
        )
        self.manager.active_stack.push(command)
        self.assertEqual(self.target.value, 1)

    def test_command_undo(self):
        command = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1
        )
        self.manager.active_stack.push(command)
        self.manager.active_stack.undo()
        self.assertEqual(self.target.value, 0)

    def test_command_redo(self):
        command = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1
        )
        self.manager.active_stack.push(command)
        self.manager.undo()
        self.manager.redo()
        self.assertEqual(self.target.value, 1)

    def test_mergeable_command_do(self):
        command1 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1,
            mergeable=True,
        )
        command2 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=2,
            mergeable=True,
        )
        self.manager.active_stack.push(command1)
        self.manager.active_stack.push(command2)
        self.assertEqual(self.target.value, 2)

    def test_mergeable_command_undo(self):
        command1 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1,
            mergeable=True,
        )
        command2 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=2,
            mergeable=True,
        )
        self.manager.active_stack.push(command1)
        self.manager.active_stack.push(command2)
        self.manager.active_stack.undo()
        self.assertEqual(self.target.value, 0)

    def test_mergeable_command_redo(self):
        command1 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1,
            mergeable=True,
        )
        command2 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=2,
            mergeable=True,
        )
        self.manager.active_stack.push(command1)
        self.manager.active_stack.push(command2)
        self.manager.active_stack.undo()
        self.manager.active_stack.redo()
        self.assertEqual(self.target.value, 2)

    def test_unmergeable_command_undo_1(self):
        command1 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1,
        )
        command2 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=2,
            mergeable=True,
        )
        self.manager.active_stack.push(command1)
        self.manager.active_stack.push(command2)
        self.manager.active_stack.undo()
        self.assertEqual(self.target.value, 1)

    def test_unmergeable_command_undo_2(self):
        command1 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=1,
            mergeable=True,
        )
        command2 = AttributeSetCommand(
            target=self.target,
            attribute='value',
            data=2,
        )
        self.manager.active_stack.push(command1)
        self.manager.active_stack.push(command2)
        self.manager.active_stack.undo()
        self.assertEqual(self.target.value, 1)
