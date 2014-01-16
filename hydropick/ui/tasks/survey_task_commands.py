#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Int, List, Supports
from apptools.undo.api import AbstractCommand

from ...model.i_survey_line import ISurveyLine

class NextSurveyLine(AbstractCommand):

    name = "Next Line"

    previous_survey_line = Supports(ISurveyLine)

    survey_lines = List(Supports(ISurveyLine))

    previous_index = Int

    def do(self):
        self.survey_lines = self.data.selected_survey_lines[:]
        self.previous_survey_line = self.data.current_survey_line

        # if nothing selected, use all survey lines
        if len(self.survey_lines) == 0:
            self.survey_lines = self.data.survey.survey_lines[:]

        # if still nothing, can't do anything reasonable, but we shouldn't
        # have been called
        if len(self.survey_lines) == 0:
            return

        if self.previous_survey_line in self.survey_lines:
            index = (self.survey_lines.index(self.previous_survey_line)+1) % \
                len(self.survey_lines)
            self.current_survey_line = self.survey_lines[index]
        else:
            self.current_survey_line = self.survey_lines[0]

        self.redo()

    def undo(self):
        if len(self.survey_lines) == 0:
            return
        self.data.current_survey_line = self.previous_survey_line

    def redo(self):
        if len(self.survey_lines) == 0:
            return
        self.data.current_survey_line = self.current_survey_line

class PreviousSurveyLine(AbstractCommand):

    name = "Previous Line"

    previous_survey_line = Supports(ISurveyLine)

    previous_index = Int

    def do(self):
        self.survey_lines = self.data.selected_survey_lines[:]
        self.previous_survey_line = self.data.current_survey_line

        # if nothing selected, use all survey lines
        if len(self.survey_lines) == 0:
            self.survey_lines = self.data.survey.survey_lines[:]

        # if still nothing, can't do anything reasonable, but we shouldn't
        # have been called...
        if len(self.survey_lines) == 0:
            return

        if self.previous_survey_line in self.survey_lines:
            index = (self.survey_lines.index(self.previous_survey_line)-1) % \
                len(self.survey_lines)
            self.current_survey_line = self.survey_lines[index]
        else:
            self.current_survey_line = self.survey_lines[-1]

        self.redo()

    def undo(self):
        if len(self.survey_lines) == 0:
            return
        self.data.current_survey_line = self.previous_survey_line

    def redo(self):
        if len(self.survey_lines) == 0:
            return
        self.data.current_survey_line = self.current_survey_line
