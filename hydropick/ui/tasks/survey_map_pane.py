#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

from traits.api import Supports
from traitsui.api import View
from pyface.tasks.api import TraitsDockPane

from ...model.i_survey import ISurvey

class SurveyMapPane(TraitsDockPane):
    """ The dock pane holding the map view of the survey """

    survey = Supports(ISurvey)

    view = View()
