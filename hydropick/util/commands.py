#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
"""
Some generic commands for use with Apptools Undo

These should probably go into apptools rather than in this project.

"""
from __future__ import absolute_import

from traits.api import Any, Bool, Str, Callable
from apptools.undo.api import AbstractCommand


class AttributeSetCommand(AbstractCommand):
    """ Command which wraps setting an attribute of an object

    This command keeps a reference to both the old and new values of the
    attribute, so this should be used with care if the values are expected to
    consume a lot of memory.

    """

    #: the attribute that we are setting
    attribute = Str

    #: the value we are setting
    value = Any

    #: whether we should merge for the same object and attribute
    mergeable = Bool(False)

    #: was the value previously undefined?
    _undefined = Bool(False)

    #: the previous value, for undoing
    _saved = Any

    def do(self):
        """ Set the value of the attribute """
        self._undefined = not hasattr(self.data, self.attribute)
        if not self._undefined:
            self._saved = getattr(self.data, self.attribute)
        setattr(self.data, self.attribute, self.value)

    def merge(self, other):
        """ Merge if mergeable and target and attribute match """
        if not self.mergeable:
            return False
        if isinstance(other, AttributeSetCommand) and other.data == self.data \
                and other.attribute == self.attribute and other.mergeable:
            self.value = other.value
            setattr(self.data, self.attribute, self.value)
            return True
        return False

    def undo(self):
        if self._undefined:
            delattr(self.data, self.attribute)
        else:
            setattr(self.data, self.attribute, self._saved)

    def redo(self):
        setattr(self.data, self.attribute, self.value)

    def _name_default(self):
        return "Set {0}".format(self.attribute)


class CallableCommand(AbstractCommand):
    """ Command which wraps a function or method call

    A corresponding undo callable must be supplied.  By default the command
    looks for an 'undo' attribute on the callable which holds the undo callable.
    The undo callable must accept the same function signature as the original
    function.

    This command keeps a reference to the arguments the function should be
    called with, and so should be used with caution

    """

    #: the callable that we are calling
    do_callable = Callable

    #: the callable that undoes the call.  This callable must accept the same
    #: arguments as the do_callable.
    undo_callable = Callable

    #: the arguments to the callable
    data = Any

    def do(self):
        args, kwargs = self.data
        self.do_callable(*args, **kwargs)

    def undo(self):
        args, kwargs = self.data
        self.undo_callable(*args, **kwargs)

    def redo(self):
        self.do()

    def _name_default(self):
        return "Call {0}".format(self.do_callable.func_name)

    def _undo_callable_default(self):
        return getattr(self.do_callable, 'undo')
