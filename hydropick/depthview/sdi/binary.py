from datetime import datetime
import struct
from StringIO import StringIO

import numpy as np


def read(filepath):
    dataset = Dataset(filepath)
    return dataset.as_dict()


class Dataset(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.parsed = False

    def as_dict(self):
        if not self.parsed:
            self.parse()

        return {
            'date': self.date,
            'filepath': self.filepath,
            'file_version': self.version,
            'frequencies': self.frequencies,
            'survey_line_number': self.survey_line_number,
        }

    def assemble_frequencies(self):
        """build clean dicts containing frequency metadata and intensity images
        for all available frequencies
        """
        frequencies = {}

        transducers = np.unique(self.trace_metadata['transducer'])
        for transducer in transducers:
            freq_dict = {}
            freq_mask = np.where(self.trace_metadata['transducer'] == transducer)

            unique_kHzs = np.unique(self.trace_metadata['kHz'][freq_mask])

            if len(unique_kHzs) > 1:
                raise RuntimeError(
                    "The file has been corrupted or there is a bug in this "
                    "parsing library. Either way, we can't figure out what "
                    "data to return."
                )
            else:
                khz = unique_kHzs[0]

            for key, array in self.trace_metadata.iteritems():
                freq_dict[key] = array[freq_mask]

            freq_dict['intensity'] = self.intensity_image[freq_mask]
            frequencies[khz] = freq_dict

        return frequencies

    def parse(self):
        with open(self.filepath, 'rb') as f:
            data = f.read()

        fid = StringIO(data)
        data_length = len(data)

        header = self.parse_file_header(fid)

        self.version = header['version']
        self.resolution_cm = header['resolution_cm']
        self.survey_line_number = header['filename']
        self.date = datetime.strptime(self.survey_line_number[:6], '%y%m%d').date()

        self.parse_records(fid, data_length)

        self.frequencies = self.assemble_frequencies()

        self.parsed = True

    def parse_file_header(self, f):
        """
        Reads in file header information. Based on the specification:
            Offset Size          File Header

            0   8 Filename       array[1..8] of Char  Original printable base filename.  All 8 chars
                                                      are used.  Formed using date and file number
                                                      with YYMMDDFF where FF = '01'..'99','9A'..'ZZ'
            8   1 Cr             Char constant 13H
            9   1 Lf             Char constant 10H
           10   1 Version        Byte                 1st nibble = major, 2nd = minor
                                                      43H = version 4.3
           11   1 ResCm          Byte                 Sample resolution in centimeters.  Used in
                                                      versions before 1.6, now zero. Superseeded
                                                      by the Rate field
        """
        f.seek(0)

        filename, cr, lf, version_byte, resolution_cm = struct.unpack('<8s2cBB', f.read(12))
        major_version = version_byte >> 4
        minor_version = version_byte & 0xF

        version = '%s.%s' % (major_version, minor_version)
        if version <= '3.2':
            raise NotImplementedError('Reading of file formats <= 3.2 Not Supported, File Version=' + str(version))

        return {
            'filename': filename,
            'version': version,
            'resolution_cm': resolution_cm,
        }

    def parse_records(self, fid, data_length):
        pre_struct, post_struct = self.record_struct()
        event_struct = [('event', None, None)]

        # intitialize trace lists
        trace_metadata = dict([
            [name, []] for name, fmt, dtype in pre_struct + post_struct + event_struct
        ])

        trace_intensities = []

        pre_fmt = '<' + ''.join([fmt for name, fmt, dtype in pre_struct])
        pre_names = [name for name, fmt, dtype in pre_struct]
        pre_size = struct.calcsize(pre_fmt)

        post_fmt = '<' + ''.join([fmt for name, fmt, dtype in post_struct])
        post_size = struct.calcsize(post_fmt)
        post_names = [name for name, fmt, dtype in post_struct]

        npos = 12
        fid.seek(npos)

        while npos < data_length:
            pre_record = struct.unpack(pre_fmt, fid.read(pre_size))
            pre_dict = dict(zip(pre_names, pre_record))

            for key, value in pre_dict.iteritems():
                trace_metadata[key].append(value)

            size = pre_dict['event_len']
            if size > 0:
                event = struct.unpack('<' + str(size) + 's', fid.read(size))[0]
            else:
                event = ''
            trace_metadata['event'].append(event)

            post_record = struct.unpack(post_fmt, fid.read(post_size))
            post_dict = dict(zip(post_names, post_record))
            for key, value in post_dict.iteritems():
                trace_metadata[key].append(value)

            fid.seek(npos + pre_dict['offset'] + 2)
            size = pre_dict['num_pnts']
            trace_intensities.append(struct.unpack('<' + str(size) + 'H', fid.read(size * 2)))
            npos = int(fid.tell())

        # convert trace_metadata lists to np arrays
        for key, value, dtype in pre_struct + post_struct + event_struct:
            trace_metadata[key] = np.array(trace_metadata[key], dtype=dtype)
        self.trace_metadata = trace_metadata

        self.intensity_image = self.build_intensity_image(trace_intensities)

    def build_intensity_image(self, trace_intensities):
        """take list of trace_intensities (each a variable length list) and
        convert to a np.array representation, padding any missing columns with
        NaNs
        """
        # trace intensity are variable length if power changes mid-trace, so we
        # need to build a clean np-array image, filling with nans
        ti_lengths = np.array([len(i) for i in trace_intensities])
        max_length = np.max(ti_lengths)
        discontinuities = np.where((ti_lengths[1:] - ti_lengths[:-1]) != 0)

        # adjust discontinuity to use as for splitting the trace_intensities
        # lists
        adjusted = [discontinuity[0] + 1 for discontinuity in discontinuities]
        starts = [0] + adjusted
        ends = adjusted + [len(trace_intensities)]

        def _padded_sub_trace(trace_intensities, start, end, to_length):
            sub_trace = np.array(trace_intensities[start:end])
            fill_nans = np.nan + np.zeros((sub_trace.shape[0], to_length - sub_trace.shape[1]))
            return np.column_stack([sub_trace, fill_nans])

        intensity_image = np.vstack([
            _padded_sub_trace(trace_intensities, start, end, max_length)
            for start, end in zip(starts, ends)
        ])

        return intensity_image

    def record_struct(self):
        pre_struct = [
            ('offset', 'H', np.int),
            ('trace_num', 'l', np.int),
            ('units', 'B', np.int),
            ('spdos_units', 'B', np.int),
            ('spdos', 'h', np.int),
            ('min_window10', 'h', np.int),
            ('max_window10', 'h', np.int),
            ('draft100', 'h', np.int),
            ('tide100', 'h', np.int),
            ('heave_cm', 'h', np.int),
            ('display_range', 'h', np.int),
            ('depth_r1', 'f', np.float),
            ('min_pnt_r1', 'f', np.float),
            ('num_pnt_r1', 'f', np.float),
            ('blanking_pnt', 'h', np.int),
            ('depth_pnt','h', np.int),
            ('range_pnt','h', np.int),
            ('num_pnts','h', np.int),
            ('clock', 'l', np.int),
            ('hour', 'B', np.int),
            ('min', 'B', np.int),
            ('sec', 'B', np.int),
            ('sec100', 'B', np.int),
            ('rate', 'l', np.int),
            ('kHz', 'f', np.float),
            ('event_len', 'B', np.int),
        ]

        post_struct = [
            ('longitude', 'd', np.float64),
            ('latitude', 'd', np.float),
            ('transducer', 'B', np.int),
            ('options', 'B', np.int),
            ('data_offset', 'B', np.int),
        ]

        if self.version >= '3.3':
            post_struct.append(('utm_x', 'd', np.float))
            post_struct.append(('utm_y', 'd', np.float))

        if self.version >= '4.0':
            post_struct.append(('cycles', 'B', np.int))
            post_struct.append(('volts', 'B', np.int))
            post_struct.append(('power', 'B', np.int))
            post_struct.append(('gain', 'B', np.int))
            post_struct.append(('previous_offset', 'H', np.int16))

        if self.version >= '4.2':
            post_struct.append(('antenna_e1', '4f', np.float))
            post_struct.append(('antenna_ht', '4f', np.float))
            post_struct.append(('draft', '4f', np.float))
            post_struct.append(('tide', '4f', np.float))

        if self.version >= '4.3':
            post_struct.append(('gps_mode', 'B', np.int))
            post_struct.append(('hdop', 'f', np.float))

        return pre_struct, post_struct
