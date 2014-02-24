#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

from __future__ import absolute_import

import os
import sys
import logging

from traits.etsconfig.etsconfig import ETSConfig
from traits.api import HasTraits, Directory, Instance, Supports

class Application(HasTraits):
    """ The main Hydropick application object """

    #: application data directory
    application_home = Directory

    #: the root logger instance
    logger = Instance('logging.Logger')

    #: application data directory
    logging_handler = Instance('logging.Handler')

    #: the PyFace GUI for the application
    gui = Supports('pyface.i_gui.IGUI')

    #: the splash-screen for the application
    splash_screen = Supports('pyface.i_splash_screen.ISplashScreen')

    #: the main task window
    task_window = Supports('pyface.tasks.task_window.TaskWindow')

    #: the main task window
    task = Instance('pyface.tasks.task.Task')

    def exception_handler(self, exc_type, exc_value, exc_traceback):
        """ Handle un-handled exceptions """
        if not isinstance(exc_value, Exception):
            # defer to usual exception handler
            sys.__excepthook__(exc_type, exc_value, exc_traceback)

        logging.error('Unhandled exception:', exc_info=(exc_type, exc_value, exc_traceback))

        from traceback import format_tb
        from pyface.api import MessageDialog

        informative = "{0}: {1}".format(exc_type.__name__, str(exc_value))
        detail = '\n'.join(format_tb(exc_traceback))
        dlg = MessageDialog(severity='error', message="Unhandled Exception",
                            informative=informative, detail=detail,
                            size=(800,600))
        dlg.open()

    def parse_arguments(self):
        import argparse
        parser = argparse.ArgumentParser(description="Hydropick: a hydrological survey editor")
        parser.add_argument('--import', help='survey data to import',
                            dest='import_', metavar='DIR')
        parser.add_argument('-v', '--verbose', action='store_const', dest='logging',
                            const=logging.INFO, help='verbose logging')
        parser.add_argument('-q', '--quiet', action='store_const', dest='logging',
                            const=logging.WARNING, help='quiet logging')
        parser.add_argument('-d', '--debug', action='store_const', dest='logging',
                            const=logging.DEBUG, help='debug logging')
        args = parser.parse_args()
        return args

    def init(self):
        # set up logging
        self.logger.addHandler(self.logging_handler)

        # parse commandline arguments
        args = self.parse_arguments()
        if args.import_:
            from ..io.import_survey import import_survey
            survey = import_survey(args.import_)
            self.task.survey = survey
        if args.logging is not None:
            self.logger.setLevel(args.logging)

    def start(self):
        self.logger.info('Starting application')

        # override the exceptionhook to display MessageDialog
        sys.excepthook = self.exception_handler

        # set up tasks
        self.task_window.add_task(self.task)
        self.task_window.open()

        # and we're done successfully
        return True

    def run(self):
        # ensure GUI instance is created
        gui = self.gui

        started = self.start()
        if started:
            self.logger.info('Starting event loop')
            gui.start_event_loop()
            self.logger.info('Event loop finished')

        self.stop()

    def stop(self):
        self.logger.info('Stopping application')

    def cleanup(self):
        logging.shutdown()

    def _application_home_default(self):
        home = ETSConfig.application_home
        if not os.path.exists(home):
            os.makedirs(home)
        return home

    def _logger_default(self):
        return logging.getLogger()

    def _logging_handler_default(self):
        from logging.handlers import RotatingFileHandler
        logfile = os.path.join(self.application_home, 'hydropick.log')
        print logfile, self.application_home
        handler = RotatingFileHandler(logfile, backupCount=5)
        handler.doRollover()
        # format output
        datefmt = '%Y%m%d:%H%M%S'
        line_fmt = '%(asctime)s :: %(name)s : %(levelname)s : %(message)s'
        formatter = logging.Formatter(line_fmt, datefmt=datefmt)
        handler.setFormatter(formatter)
        return handler

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
