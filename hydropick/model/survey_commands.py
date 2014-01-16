#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Int, Supports
from apptools.undo.api import AbstractCommand

from .i_survey_line_group import ISurveyLineGroup

class AddSurveyLineGroup(AbstractCommand):

    name = "New Group"

    group = Supports(ISurveyLineGroup)

    def do(self):
        print 'doing add survey line group'
        self.data.add_survey_line_group(self.group)
        print self.data.survey_line_groups

    def undo(self):
        self.data.delete_survey_line_group(self.group)

    def redo(self):
        self.do()

class DeleteSurveyLineGroup(AbstractCommand):

    name = "Delete Group"

    group = Supports(ISurveyLineGroup)

    _index = Int

    def do(self):
        self._index = self.data.delete_survey_line_group(self.group)

    def undo(self):
        self.data.add_survey_line_group(self.group)

    def redo(self):
        self.do()
