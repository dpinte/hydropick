#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Instance, Int, List
from apptools.undo.api import AbstractCommand

from .i_survey import ISurvey
from .i_survey_line import ISurveyLine
from .i_survey_line_group import ISurveyLineGroup

class AddSurveyLineGroup(AbstractCommand):
    """ Add a new SurveyLineGroup to the Survey """

    name = "New Group"

    #: the survey we are working with
    data = Instance(ISurvey)

    #: the group we are adding
    group = Instance(ISurveyLineGroup)

    def do(self):
        self.data.add_survey_line_group(self.group)

    def undo(self):
        self.data.delete_survey_line_group(self.group)

    def redo(self):
        self.do()


class DeleteSurveyLineGroup(AbstractCommand):
    """ Remove a SurveyLineGroup to the Survey """

    name = "Delete Group"

    #: the survey we are working with
    data = Instance(ISurvey)

    #: the group we are removing
    group = Instance(ISurveyLineGroup)

    #: the index of the group we are removing in the list of groups
    _index = Int

    def do(self):
        self._index = self.data.delete_survey_line_group(self.group)

    def undo(self):
        self.data.add_survey_line_group(self.group)

    def redo(self):
        self.do()


class AddSurveyLinesToGroup(AbstractCommand):
    """ Add a new SurveyLines to a SurveyLineGroup """

    name = "Add Lines to Group"

    #: the survey line group we are working with
    data = Instance(ISurveyLineGroup)

    #: the lines we are adding to the group
    lines = List(Instance(ISurveyLine))

    #: the original set of lines in the group
    _old_state = List(Instance(ISurveyLine))

    def do(self):
        self._old_state = self.data.survey_lines[:]
        self.data.add_survey_lines(self.lines)

    def undo(self):
        self.data.survey_lines[:] = self._old_state

    def redo(self):
        self.do()


class RemoveSurveyLinesFromGroup(AbstractCommand):
    """ Remove SurveyLines from a SurveyLineGroup """

    name = "Remove Lines from Group"

    #: the survey line group we are working with
    data = Instance(ISurveyLineGroup)

    #: the lines we are removing from the group
    lines = List(Instance(ISurveyLine))

    #: the original set of lines in the group
    _old_state = List(Instance(ISurveyLine))

    def do(self):
        self._old_state = self.data.survey_lines[:]
        self.data.remove_survey_lines(self.lines)

    def undo(self):
        self.data.survey_lines[:] = self._old_state

    def redo(self):
        self.do()
