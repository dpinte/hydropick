''' Unit tests for surveydatasession

'''
import os
import shutil
import tempfile
import unittest
import numpy as np

from traits.interface_checker import InterfaceError
from traits import has_traits
from hydropick.io import survey_io


class TestAlgorithms(unittest.TestCase):

    def setUp(self):
        has_traits.CHECK_INTERFACES = 1
        self.test_dir = os.path.dirname(__file__)
        linename = '12030101'
        filename = os.path.join(self.test_dir, 'files', linename + '.bin')
        self.tempdir = tempfile.mkdtemp()
        self.h5file = os.path.join(self.tempdir, 'test.h5')
        survey_io.import_survey_line_from_file(filename, self.h5file, linename)
        self.survey_line = survey_io.read_survey_line_from_hdf(self.h5file,
                                                               linename)
        self.survey_line.load_data(self.h5file)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def get_classes(self):
        from hydropick.model import algorithms
        name_list = algorithms.ALGORITHM_LIST
        classes = [getattr(algorithms, cls_name) for cls_name in name_list]
        names = [cls().name for cls in classes]
        return classes

    def test_provides(self):
        ''' check that the algorithms provide the IAlgoritm interface
        '''
        has_traits.CHECK_INTERFACES = 2
        try:
            from hydropick.model import algorithms
            reload(algorithms)
        except InterfaceError as err:
            self.assertTrue(False, msg='Interface Error: {}'.format(err))

    def test_existence(self):
        ''' check all listed algorithms are defined'''
        try:
            self.get_classes()
        except AttributeError as err:
            self.assertTrue(False, msg='undefined: {}'.format(err))

    def test_process_line(self):
        ''' check the process_line returns correct arrays for all algorithms'''
        try:
            class_list = self.get_classes()
            for cls in class_list:
                trace_array, depth_array = cls().process_line(self.survey_line)
                self.assertIsInstance(np.asarray(trace_array), np.ndarray,
                                    msg='cannot convert to array')
                self.assertIsInstance(np.asarray(depth_array), np.ndarray,
                                    msg='cannot convert to array')
                self.assertEqual(len(trace_array),len(depth_array))
        except AttributeError as err:
            self.assertTrue(False, msg='undefined: {}'.format(err))


if __name__ == "__main__":
    # from package use "python -m unittest discover -v -s ./tests/"
    unittest.main()
