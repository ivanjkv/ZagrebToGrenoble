"""
Functions for reading Tecmag .tnt data files.
"""

__author__ = "ijakovac@phy.hr"
__developer_doc__ = """
Tecmag .tnt file format information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Tecmag .tnt file format is documented with C pseudo-code in the file
"A1 - TNMR File Format.doc" distributed with the TNMR software.

This file is based on the
`pytnt module <https://www.github.com/chatcannon/pytnt>`_.
Please inform upstream if you find a bug or to request additional features.

This file was modified to read Sequence part of .tnt file (PSEQ tag).

"""

import re
import io

import numpy as np

class BytesIO2(io.BytesIO):
    # upgrade to standard io.BytesIO class to read strings with preceding UInt32 lengths
    def __init__(self):
        super()

    def read_string(self):
        length = np.frombuffer(self.read(4), '<u4')[0]
        return np.frombuffer(self.read(length), 'S{}'.format(length))[0] if length else b''

class TNTReader():

    TNTMAGIC_RE = re.compile(b"^TNT1\.\d\d\d$")
    
    TNTMAGIC = np.dtype('S8')
    TNTTLV = np.dtype([('tag', 'S4'), ('bool', '<u4'), ('length', '<u4')])
    
    TNTTMAG = np.dtype([
        ('npts', '<i4', 4),
        ('actual_npts', '<i4', 4),
        ('acq_points', '<i4'),
        ('npts_start', '<i4', 4),
        ('scans', '<i4'),
        ('actual_scans', '<i4'),
        ('dummy_scans', '<i4'),
        ('repeat_times', '<i4'),
        ('sadimension', '<i4'),
        ('samode', '<i4'),
    
        ('magnet_field', '<f8'),
        ('ob_freq', '<f8', 4),
        ('base_freq', '<f8', 4),
        ('offset_freq', '<f8', 4),
        ('ref_freq', '<f8'),
        ('NMR_frequency', '<f8'),
        ('obs_channel', '<i2'),
        ('space2', 'V42'),
    
        ('sw', '<f8', 4),
        ('dwell', '<f8', 4),
        ('filter', '<f8'),
        ('experiment_time', '<f8'),
        ('acq_time', '<f8'),
        ('last_delay', '<f8'),
        ('spectrum_direction', '<i2'),
        ('hardware_sideband', '<i2'),
        ('Taps', '<i2'),
        ('Type', '<i2'),
        ('bDigRec', '<u4'),
        ('nDigitalCenter', '<i4'),
        ('space3', 'V16'),
    
        ('transmitter_gain', '<i2'),
        ('receiver_gain', '<i2'),
        ('NumberOfReceivers', '<i2'),
        ('RG2', '<i2'),
        ('receiver_phase', '<f8'),
        ('space4', 'V4'),
    
        ('set_spin_rate', '<u2'),
        ('actual_spin_rate', '<u2'),
    
        ('lock_field', '<i2'),
        ('lock_power', '<i2'),
        ('lock_gain', '<i2'),
        ('lock_phase', '<i2'),
        ('lock_freq_mhz', '<f8'),
        ('lock_ppm', '<f8'),
        ('H2O_freq_ref', '<f8'),
        ('space5', 'V16'),
    
        ('set_temperature', '<f8'),
        ('actual_temperature', '<f8'),
    
        ('shim_units', '<f8'),
        ('shims', '<i2', 36),
        ('shim_FWHM', '<f8'),
    
        ('HH_dcpl_attn', '<i2'),
        ('DF_DN', '<i2'),
        ('F1_tran_mode', '<i2', 7),
        ('dec_BW', '<i2'),
        ('grd_orientation', 'a4'),
        ('LatchLP', '<i4'),
        ('grd_Theta', '<f8'),
        ('grd_Phi', '<f8'),
        ('space6', 'V264'),
    
        ('start_time', '<u4'),
        ('finish_time', '<u4'),
        ('elapsed_time', '<i4'),
    
        ('date', 'S32'),
        ('nuclei', 'S16', 4),
        ('sequence', 'S32'),
        ('lock_solvent', 'S16'),
        ('lock_nucleus', 'S16')
    ])
    
    
    TNTGRIDANDAXIS = np.dtype([
        ('majorTickInc', '<f8', 12),
        ('minorIntNum', '<i2', 12),
        ('labelPrecision', '<i2', 12),
        ('gaussPerCentimeter', '<f8'),
        ('gridLines', '<i2'),
        ('axisUnits', '<i2'),
        ('showGrid', '<u4'),
        ('showGridLabels', '<u4'),
        ('adjustOnZoom', '<u4'),
        ('showDistanceUnits', '<u4'),
        ('axisName', 'S32'),
        ('space', 'V52'),
    ])
    
    
    TNTTMG2 = np.dtype([
        ('real_flag', '<u4'),
        ('imag_flag', '<u4'),
        ('magn_flag', '<u4'),
        ('axis_visible', '<u4'),
        ('auto_scale', '<u4'),
        ('line_display', '<u4'),
        ('show_shim_units', '<u4'),
    
        ('integral_display', '<u4'),
        ('fit_display', '<u4'),
        ('show_pivot', '<u4'),
        ('label_peaks', '<u4'),
        ('keep_manual_peaks', '<u4'),
        ('label_peaks_in_units', '<u4'),
        ('integral_dc_average', '<u4'),
        ('integral_show_multiplier', '<u4'),
        ('Boolean_space', '<u4', 9),
    
        ('all_ffts_done', '<u4', 4),
        ('all_phase_done', '<u4', 4),
    
        ('amp', '<f8'),
        ('ampbits', '<f8'),
        ('ampCtl', '<f8'),
        ('offset', '<i4'),
    
        ('axis_set', TNTGRIDANDAXIS),
    
        ('display_units', '<i2', 4),
        ('ref_point', '<i4', 4),
        ('ref_value', '<f8', 4),
        ('z_start', '<i4'),
        ('z_end', '<i4'),
        ('z_select_start', '<i4'),
        ('z_select_end', '<i4'),
        ('last_zoom_start', '<i4'),
        ('last_zoom_end', '<i4'),
        ('index_2D', '<i4'),
        ('index_3D', '<i4'),
        ('index_4D', '<i4'),
    
        ('apodization_done', '<i4', 4),
        ('linebrd', '<f8', 4),
        ('gaussbrd', '<f8', 4),
        ('dmbrd', '<f8', 4),
        ('sine_bell_shift', '<f8', 4),
        ('sine_bell_width', '<f8', 4),
        ('sine_bell_skew', '<f8', 4),
        ('Trapz_point_1', '<i4', 4),
        ('Trapz_point_2', '<i4', 4),
        ('Trapz_point_3', '<i4', 4),
        ('Trapz_point_4', '<i4', 4),
        ('trafbrd', '<f8', 4),
        ('echo_center', '<i4', 4),
    
        ('data_shift_points', '<i4'),
        ('fft_flag', '<i2', 4),
        ('unused', '<f8', 8),
        ('pivot_point', '<i4', 4),
        ('cumm_0_phase', '<f8', 4),
        ('cumm_1_phase', '<f8', 4),
        ('manual_0_phase', '<f8'),
        ('manual_1_phase', '<f8'),
        ('phase_0_value', '<f8'),
        ('phase_1_value', '<f8'),
        ('session_phase_0', '<f8'),
        ('session_phase_1', '<f8'),
    
        ('max_index', '<i4'),
        ('min_index', '<i4'),
        ('peak_threshold', '<f4'),
        ('peak_noise', '<f4'),
        ('integral_dc_points', '<i2'),
        ('integral_label_type', '<i2'),
        ('integral_scale_factor', '<f4'),
        ('auto_integrate_shoulder', '<i4'),
        ('auto_integrate_noise', '<f8'),
        ('auto_integrate_threshold', '<f8'),
        ('s_n_peak', '<i4'),
        ('s_n_noise_start', '<i4'),
        ('s_n_noise_end', '<i4'),
        ('s_n_calculated', '<f4'),
    
        ('Spline_point', '<i4', 14),
        ('Spline_point_avr', '<i2'),
        ('Poly_point', '<i4', 8),
        ('Poly_point_avr', '<i2'),
        ('Poly_order', '<i2'),
    
        ('space', 'V610'),
    
        ('line_simulation_name', 'S32'),
        ('integral_template_name', 'S32'),
        ('baseline_template_name', 'S32'),
        ('layout_name', 'S32'),
        ('relax_information_name', 'S32'),
        ('username', 'S32'),
        ('user_string_1', 'S16'),
        ('user_string_2', 'S16'),
        ('user_string_3', 'S16'),
        ('user_string_4', 'S16')
    ])

    PSEQROW = np.dtype([
                ('Number of Columns', '<V4'),
                ('Address', '<V4'),
                ('BitLength', '<V4'),
                ('Icon Library Type', 'V4'),
                ('Visible Flag', '<V4'),
                ('Private Data', '<V4'),
                ('Group', '<V4'),
    ])


    def __init__(self, filename):
        """
        Read a Tecmag .tnt data file.
    
        Parameters
        ----------
        filename : str
            Name of file to read from
    
        Returns
        -------
        dic : dict
            Dictionary of Tecmag parameters.
        data : ndarray
            Array of NMR data.
    
        """
        self.tnt_sections = dict()
    
        with open(filename, 'rb') as tntfile:
    
            # Check if .tnt file is valid
            tntmagic = np.frombuffer(tntfile.read(self.TNTMAGIC.itemsize),
                                     self.TNTMAGIC, count=1)[0]

            if not self.TNTMAGIC_RE.match(tntmagic):
                err = ("Invalid magic number (is '%s' really TNMR file?): %s" %
                       (filename, tntmagic))
                raise ValueError(err)
            self.version = tntmagic.decode()    #determine .tnt file version

            # Read in the section headers
            tnthdrbytes = tntfile.read(self.TNTTLV.itemsize)
            while(self.TNTTLV.itemsize == len(tnthdrbytes)):
                tlv = np.frombuffer(tnthdrbytes, self.TNTTLV)[0]
                data_length = tlv['length']
                hdrdict = {'offset': tntfile.tell(),
                           'length': data_length,
                           'bool': bool(tlv['bool'])}
                if tlv['tag'].decode() == 'PSEQ':
                    # PSEQ stucture doesn't have length parameter, so we go back 4 bytes.
                    tntfile.seek(-4, 1)
                    self.start = tntfile.tell()
                    hdrdict['data'] = tntfile.read()
                    hdrdict['length'] = len(hdrdict['data'])
                else:
                    hdrdict['data'] = tntfile.read(data_length)
    
    
                self.tnt_sections[tlv['tag'].decode()] = hdrdict
                tnthdrbytes = tntfile.read(self.TNTTLV.itemsize)
    
    
        assert(self.tnt_sections['TMAG']['length'] == self.TNTTMAG.itemsize)
        self.tmag = np.frombuffer(self.tnt_sections['TMAG']['data'], self.TNTTMAG, count=1)[0]
    
        assert(self.tnt_sections['DATA']['length'] == self.tmag['actual_npts'].prod() * 8)
    
        self.data = np.memmap(filename, np.dtype('<c8'), mode='c', offset=self.tnt_sections['DATA']['offset'],
                         shape=self.tmag['actual_npts'].prod())
        self.data = np.reshape(self.data, self.tmag['actual_npts'], order='F')
    
        assert(self.tnt_sections['TMG2']['length'] == self.TNTTMG2.itemsize)
        self.tmg2 = np.frombuffer(self.tnt_sections['TMG2']['data'], self.TNTTMG2, count=1)[0]

    
        self.params = dict()
        # save TMAG data into dic
        for name in self.TNTTMAG.names:
            if not name.startswith('space'):
                self.params[name] = self.tmag[name]
        # save TMAG data into dic
        for name in self.TNTTMG2.names:
            if name not in ['Boolean_space', 'unused', 'space', 'axis_set']:
               self.params[name] = self.tmg2[name]
        for name in self.TNTGRIDANDAXIS.names:
            if not name.startswith('space'):
                self.params[name] = self.tmg2['axis_set'][name]
    
        # update pseq data
        self.params.update(self.pseq_read(self.tnt_sections['PSEQ']['data']))


    def pseq_read(self, data):
        dic = dict()
        
        binary = BytesIO2()
        binary.write(data)
        binary.seek(0)

        dic['SequenceID'] = np.frombuffer(binary.read(8), 'S8')[0].decode()
        dic['File Name'] = binary.read_string()
    
        if dic['SequenceID'][:4] == '1.18':
            binary.seek(8, 1)
            dic['E-mail'] = binary.read_string()
    
        dic['NRows'] = np.frombuffer(binary.read(4), '<u4')[0]
        dic['NCols'] = np.frombuffer(binary.read(4), '<u4')[0]
    
        # Read TNMR sequence and store it into dictionary
        dic['Sequence'] = dict()

        for row in range(dic['NRows']):
            # 28 bytes of useless data
            np.frombuffer(binary.read(self.PSEQROW.itemsize), self.PSEQROW, count = 1)[0]
    
            # Read row index and use the row name as a new (sub)dictionary
            binary.read_string()
            row_name = binary.read_string().decode()
            dic['Sequence'][row_name] = dict()
    
            for column in range(dic['NCols']):
                # Read a column value and use it as a new key to store tables.
                col_name = binary.read_string().decode()
                # [value, 0D-4D table names]
                values = [col_name]
                for dim in range(5):
                    values.append(binary.read_string().decode())
                    binary.seek(4,1)
                # whitespace
                binary.seek(16,1)
                dic['Sequence'][row_name][column] = values
    
                # [Acq row, True (1) column] has some additional data
                if row_name == 'Acq' and col_name == '1':
                    for i in range(6):
                        binary.read_string()
                    binary.seek(1,1)
        
        # Read TNMR tables and store them into Dictionary
        # Old TNMR has integer N followed by N tables
        # TNT1.003 version has 128 blanks than N followed by N*4 bytes of blank space before integer number of tables
        # TNT1.007 version has 128 blanks than N followed by N*4 bytes of blank space before integer number of tables
        # TNT1.008 version has integer N followed by N*4 bytes of blank space before integer number of tables
        if self.version in ['TNT1.003', 'TNT1.004', 'TNT1.005', 'TNT1.006', 'TNT1.007']:
            binary.seek(128,1)
            binary.seek(np.frombuffer(binary.read(4), '<u4')[0]*4,1)
            dic['NTables'] = np.frombuffer(binary.read(4), '<u4')[0]
        elif self.version == 'TNT1.008':
            binary.seek(np.frombuffer(binary.read(4), '<u4')[0]*4,1)
            dic['NTables'] = np.frombuffer(binary.read(4), '<u4')[0]
        else:
            dic['NTables'] = np.frombuffer(binary.read(4), '<u4')[0]

        # Create dictionaries to store tables
        dic['Tables'] = dict()
        dic['+ Adds'] = dict()
        dic['Unknowns'] = dict()

        for table in range(dic['NTables']):
            tab_name = binary.read_string().decode('ansi')
            dic['Tables'][tab_name] = [i for i in binary.read_string().decode().replace(' ','\r\n').split('\r\n')]
            if binary.read_string() == b'': # can't compare versions; exception occurs when an old file is saved by new TNMR
                binary.seek(12,1) # 16 bytes of empty space (-4 because string already read)
                binary.seek(56,1) # some data / find meaning!
            else:
                # binary.read_string() # '+ Add' (string already read)
                dic['+ Adds'][tab_name] = binary.read_string() # '+ Add 'data table'
                binary.read_string() # 'Every pass'
                binary.seek(36,1) # some data / find meaning!
                dic['Unknowns'] = [binary.read_string() for _ in range(3)]
                if self.version == 'TNT1.003':
                    binary.seek(4,1) # skip 1 integer in TNT1.003 version
                else:
                    binary.seek(12,1) # skip 3 integers

        # Now reading the rest of the file...
        
        dic['Parameters'] = dict() # dictionary for sequence parameters                
        if self.version in ['TNT1.003', 'TNT1.004', 'TNT1.005', 'TNT1.006', 'TNT1.007']:
            binary.read(4)       # '1' - len of following data
            binary.read_string() # 'Sequence' tag
            [binary.read_string() for i in range(np.frombuffer(binary.read(4), '<u4')[0])] # names of N sequence parameters such as trig, atten,...
        if self.version == 'TNT1.008': binary.seek(4,1) # in new version there is no 'Sequence' tag, just 4 blank spaces
        dic['NParameters'] = np.frombuffer(binary.read(4), '<u4')[0]
        for i in range(dic['NParameters']):
            parameter_name = binary.read_string().decode('ansi')
            dic['Parameters'][parameter_name] = dict()
            dic['Parameters'][parameter_name]['Flag'] = np.frombuffer(binary.read(4), '<u4')[0]
            dic['Parameters'][parameter_name]['Value'] = binary.read_string().decode('ansi')
            dic['Parameters'][parameter_name]['Type'] = np.frombuffer(binary.read(4), '<u4')[0] # 6 - time, 4 - double
            dic['Parameters'][parameter_name]['Minumum'] = binary.read_string().decode('ansi')
            dic['Parameters'][parameter_name]['Maximum'] = binary.read_string().decode('ansi')
            binary.seek(12,1) # blanks
            binary.read_string() # parameter name again
            dic['Parameters'][parameter_name]['Default'] = binary.read_string().decode('ansi')
            binary.seek(16,1) # blanks

        temp = binary.read() # read the rest of the file
        rest = BytesIO2()
        rest.write(temp)
        rest.seek(temp.find(b'CMNT')+4) # find 'Comment' tag and skip it
        dic['Comments'] = 'No comments'
        if np.frombuffer(rest.read(4), '<u4')[0]:
            dic['Comments'] = rest.read_string().decode('ansi')
                                        
        return dic



