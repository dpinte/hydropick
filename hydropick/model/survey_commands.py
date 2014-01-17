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

    name = "New Group"

    data = Instance(ISurvey)

    group = Instance(ISurveyLineGroup)

    def do(self):
        self.data.add_survey_line_group(self.group)

    def undo(self):
        self.data.delete_survey_line_group(self.group)

    def redo(self):
        self.do()


class DeleteSurveyLineGroup(AbstractCommand):

    name = "Delete Group"

    data = Instance(ISurvey)

    group = Instance(ISurveyLineGroup)

    _index = Int

    def do(self):
        self._index = self.data.delete_survey_line_group(self.group)

    def undo(self):
        self.data.add_survey_line_group(self.group)

    def redo(self):
        self.do()


class AddSurveyLinesToGroup(AbstractCommand):

    name = "Add Lines to Group"

    data = Instance(ISurveyLineGroup)

    lines = List(Instance(ISurveyLine))

    _old_state = List(Instance(ISurveyLine))

    def do(self):
        self._old_state = self.data.survey_lines[:]
        self.data.add_survey_lines(self.lines)

    def undo(self):
        self.data.survey_lines[:] = self._old_state

    def redo(self):
        self.do()


class RemoveSurveyLinesFromGroup(AbstractCommand):

    name = "Remove Lines from Group"

    data = Instance(ISurveyLineGroup)

    lines = List(Instance(ISurveyLine))

    _old_state = List(Instance(ISurveyLine))

    def do(self):
        self._old_state = self.data.survey_lines[:]
        self.data.remove_survey_lines(self.lines)

    def undo(self):
        self.data.survey_lines[:] = self._old_state

    def redo(self):
        self.do()
