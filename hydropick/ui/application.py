#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from traits.api import HasTraits, Instance, Supports

class Application(HasTraits):
    """ The main application object """

    #: the PyFace GUI for the application
    gui = Supports('pyface.i_gui.IGUI')

    #: the splash-screen for the application
    splash_screen = Supports('pyface.i_splash_screen.ISplashScreen')

    #: the main task window
    task_window = Supports('pyface.tasks.task_window.TaskWindow')

    #: the main task window
    task = Instance('pyface.tasks.task.Task')

    def parse_arguments(self):
        import argparse
        parser = argparse.ArgumentParser(description="Hydropick: a hydrological survey editor")
        parser.add_argument('--import', help='survey data to import',
                            dest='import_', metavar='DIR')
        args = parser.parse_args()
        return args

    def start(self):
        args = self.parse_arguments()
        if hasattr(args, 'import_'):
            from ..io.import_survey import import_survey
            survey = import_survey(args.import_)
            self.task.survey = survey
        self.task_window.add_task(self.task)
        self.task_window.open()
        return True

    def run(self):
        # ensure GUI instance is created
        gui = self.gui

        started = self.start()
        if started:
            gui.start_event_loop()

        self.stop()

    def stop(self):
        pass

    def _gui_default(self):
        from pyface.api import GUI
        return GUI(splash_screen=self.splash_screen)

    def _task_window_default(self):
        from pyface.tasks.api import TaskWindow
        window = TaskWindow(size=(960, 720))
        return window

    def _task_default(self):
        from .tasks.survey_task import SurveyTask
        return SurveyTask()
