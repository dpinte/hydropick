
from pyface.api import GUI
from pyface.tasks.api import TaskWindow

from hydropick.ui.tasks.survey_task import SurveyTask

def main():
    """ A simple main function that creates a single HydropickTask for testing """

    gui = GUI()

    task = SurveyTask()
    window = TaskWindow(size=(960, 720))
    window.add_task(task)

    window.open()

    gui.start_event_loop()


if __name__ == '__main__':
    main()
