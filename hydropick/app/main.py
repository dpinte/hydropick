#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#


# ensure Qt backend so Tasks works
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = 'qt4'

from hydropick.ui.application import Application

def main():
    """ A simple main function that creates a single HydropickTask for testing """

    app = Application()
    app.run()


if __name__ == '__main__':
    main()
