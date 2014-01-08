
import sys

from pyface.api import GUI
from pyface.tasks.api import TaskWindow

from hydropick.io.import_survey import import_survey
from hydropick.ui.tasks.survey_task import SurveyTask

def main():
    """ A simple main function that creates a single HydropickTask for testing """

    gui = GUI()

    survey = import_survey(sys.argv[1])
    task = SurveyTask(survey=survey)
    window = TaskWindow(size=(960, 720))
    window.add_task(task)

    window.open()

    gui.start_event_loop()


if __name__ == '__main__':
    main()
