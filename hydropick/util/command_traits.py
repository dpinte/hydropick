#
# (C) Copyright 2014 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is open source software distributed according to the terms in
# LICENSE.txt
#
"""
Traits which facilitate use of Apptools Undo

This module provides a couple of trait Property factories to simplify the use
of Apptools Undo in the common case of wanting a trait which when set generates
an AttributeSetCommand and passes it to an UndoManager.

These should probably go into apptools rather than in this project.

"""

from __future__ import absolute_import

from traits.api import Property
from .commands import AttributeSetCommand


def UndoingDelegate(delegate, attribute, undo_manager, name=None,
                    mergeable=False, trait=None, command=AttributeSetCommand,
                    **metadata):
    """ Delegate-style Property which mediates changes via an undo manager

    This trait is intended for use on ModelView-style classes, where changes to
    the UndoingDelegate are turned into commands targeted against the underlying
    object and attribute and added to an undo manager's stack.

    Parameters
    ----------

    delegate :
        The name of the trait holding the target object.
    attribute :
        The name of the attribute on the target object.
    undo_manager :
        The name of the trait holding the undo manager to use.
    mergeable :
        Whether or not to merge consecutive sets into a single command.
    name :
        The display name for the command.
    trait :
        A trait to use for validation.
    command :
        A command factory, default is AttributeSetCommand

    The command factory will be passed keyword arguments of `data` (the object
    that the trait is on), `attribute`, `value`, `name` and `mergeable`.

    """
    depends_on = delegate+'.'+attribute

    def fget(object):
        data = getattr(object, delegate)
        return getattr(data, attribute)

    def fset(object, value):
        data = getattr(object, delegate)
        cmd = command(data=data, attribute=attribute, value=value, name=name,
                      mergeable=mergeable)
        manager = getattr(object, undo_manager)
        manager.active_stack.push(cmd)

    return Property(fget=fget, fset=fset, force=True, trait=trait,
                    depends_on=depends_on, **metadata)


def Undoable(undo_manager, mergeable=False, trait=None, **metadata):
    """ Property which mediates changes via an undo manager

    This trait wraps a shadow attribute so that all setattrs are mediated
    via an UndoManager.  This is intended to provide trait on a class
    that you want to automatically generate Apptools Undo commands.

    Parameters
    ----------

    undo_manager :
        The name of the trait holding the undo manager to use.
    mergeable :
        Whether or not to merge consecutive sets into a single command.
    trait :
        A trait to use for validation.

    """

    if trait is None and not isinstance(undo_manager, basestring):
        # treat undo_manager as a trait type & shift args
        trait = undo_manager
        undo_manager = mergeable

    def fget(object, name):
        return getattr(object, name+'_')

    def fset(object, name, value):
        command = AttributeSetCommand(data=object, attribute=name+'_', value=value,
                                    mergeable=mergeable)
        manager = getattr(object, undo_manager)
        manager.active_stack.push(command)

    return Property(fget=fget, fset=fset, force=True, trait=trait)
