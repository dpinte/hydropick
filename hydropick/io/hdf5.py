import contextlib

import numpy as np
import sdi
import tables


class HDF5Backend(object):
    """Read/write access for HDF5 data store."""

    def __init__(self, filepath):
        self.filepath = filepath
        self.hydropick_format_version = 1

    def import_binary_file(self, bin_file):
        data = sdi.binary.read(bin_file)
        x = data['frequencies'][-1]['interpolated_easting']
        y = data['frequencies'][-1]['interpolated_northing']
        coords = np.vstack((x, y)).T
        line_name = data['survey_line_number']
        with self._open_file('a') as f:
            line_group = self._get_survey_line_group(f, line_name)
            f.create_array(line_group, 'navigation_line', coords)
            f.flush()

        self._write_freq_dicts(line_name, data['frequencies'])

    def read_frequency_data(self, line_name):
        try:
            with self._open_file('r') as f:
                frequencies_group = self._get_frequencies_group(f, line_name)
                freq_data = [
                    dict([
                        (array.name, array.read())
                        for array in freq
                    ] + [('kHz', np.float(freq._v_name[4:].replace('_', '.')))])
                    for freq in frequencies_group
                ]
        except tables.FileModeError:
            raise tables.NoSuchNodeError
        return freq_data

    def read_survey_line_coords(self, line_name):
        try:
            with self._open_file('r') as f:
                line_group = self._get_survey_line_group(f, line_name)
                coords = line_group.navigation_line.read()
        except tables.FileModeError:
            raise tables.NoSuchNodeError
        return coords

    def _get_frequency_group(self, f, line_name, khz):
        """returns the group for the collection of frequency data for a survey line"""
        frequencies_group = self._get_frequencies_group(f, line_name)
        frequency_label = 'khz_' + str(khz).replace('.', '_')
        try:
            frequency_group = f.get_node(frequencies_group, frequency_label)
        except tables.NoSuchNodeError:
            frequency_group = f.create_group(frequencies_group, frequency_label)
        return frequency_group

    def _get_frequencies_group(self, f, line_name):
        """returns the group for the collection of frequency data for a survey line"""
        survey_line_group = self._get_survey_line_group(f, line_name)
        try:
            frequency_group = f.get_node(survey_line_group, 'frequencies')
        except tables.NoSuchNodeError:
            frequency_group = f.create_group(survey_line_group, 'frequencies')
        return frequency_group

    def _get_survey_lines_group(self, f):
        """returns the group for the collection of survey_lines - creating it if necessary"""
        try:
            survey_lines_group = f.get_node('/survey_lines')
        except tables.NoSuchNodeError:
            survey_lines_group = f.create_group(f.root, 'survey_lines')
        return survey_lines_group

    def _get_survey_line_group(self, f, line_name):
        """returns a group for a specific survey_line - creating it if necessary"""
        survey_lines = self._get_survey_lines_group(f)
        group_label = 'line_' + line_name
        try:
            line_group = f.get_node(survey_lines, group_label)
        except tables.NoSuchNodeError:
            line_group = f.create_group(survey_lines, group_label)
        return line_group

    @contextlib.contextmanager
    def _open_file(self, mode):
        """context manager that opens a file and also checks that the hydropick
        version number is correct
        """
        with tables.open_file(self.filepath, mode) as f:
            if f.get_filesize() <= 10000 and len(f.list_nodes('/')) == 0:
                f.root._v_attrs.version = self.hydropick_format_version
            if not hasattr(f.root._v_attrs, 'version') or f.root._v_attrs.version != self.hydropick_format_version:
                # TODO: implement upgrade code
                raise NotImplementedError(
                    "Unsupported version of hdf5 backend file. Delete file and try again."
                )
            else:
                yield f

    def _write_freq_dicts(self, line_name, freq_dicts):
        with self._open_file('a') as f:
            for freq_dict in freq_dicts:
                khz = freq_dict.pop('kHz')
                freq_group = self._get_frequency_group(f, line_name, khz)
                for key, value in freq_dict.iteritems():
                    f.create_array(freq_group, key, value)
            f.flush()
