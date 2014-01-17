#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

import os

# ensure Qt backend so Tasks works
from traits.etsconfig.etsconfig import ETSConfig
ETSConfig.toolkit = 'qt4'

# company should be Texas Water Development Board
ETSConfig.company = 'twdb'
ETSConfig.application_home = os.path.join(ETSConfig.application_data, 'hydropick')

def main():
    """ A simple main function that creates an application for testing """
    from hydropick.ui.application import Application
    app = Application()
    app.init()
    app.run()
    app.cleanup()


if __name__ == '__main__':
    main()
