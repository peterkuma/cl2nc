#!/usr/bin/env python3

__version__ = '3.7.0'

import sys
import signal
signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))
import logging
logging.basicConfig(format='%(name)s: %(message)s')
log = logging.getLogger(sys.argv[0])
import os
import traceback
import re
import itertools
import argparse
import datetime as dt
import numpy as np
from netCDF4 import Dataset

NA_INT32 = -1<<31
NA_INT64 = -1<<63

NA_NETCDF = {
    'i4': NA_INT32,
    'i8': NA_INT64,
    'f4': np.nan,
    'f8': np.nan,
}

re_file_time = re.compile(b'^.*\.(?P<year>\d{2})(?P<month>\d\d)(?P<day>\d\d)\.dat$')
re_line_time_1 = re.compile(b'^-?(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d) (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)$')
re_line_time_2 = re.compile(b'^(?P<unix_time>\d*\.?\d*)$')
re_line_time_3 = re.compile(b'^= (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)$')
re_line1 = re.compile(b'^\x01?(?P<id>CL)(?P<unit>.)(?P<software_level>\d\d\d)(?P<message_number>\d)(?P<message_subclass>\d)\x02?$')
re_line1ct = re.compile(b'^\x01?(?P<id>CT)(?P<unit>.)(?P<software_level>\d\d)(?P<message_number>\d)(?P<message_subclass>\d)\x02?$')
re_line2 = re.compile(b'^(?P<detection_status>.)(?P<self_check>.) (?P<cbh_or_vertical_visibility>.{5}) (?P<cbh2_or_highest_signal>.{5}) (?P<cbh_3>.{5}) (?P<status_alarm>.{4})(?P<status_warning>.{4})(?P<status_internal>.{4})$')
re_line2ct = re.compile(b'^(?P<detection_status>.)(?P<self_check>.) (?P<cbh_or_vertical_visibility>.{5}) (?P<cbh2_or_highest_signal>.{5}) (?P<cbh_3>.{5}) (?P<status_alarm>.{2})(?P<status_warning>.{3})(?P<status_internal>.{3})$')
re_line3 = re.compile(b'^ ?(?P<sky_detection_status>.?.) +(?P<layer1_height>.{4}) +(?P<layer2_cloud_amount>.) +(?P<layer2_height>.{4}) +(?P<layer3_cloud_amount>.) +(?P<layer3_height>.{4}) +(?P<layer4_cloud_amount>.) +(?P<layer4_height>.{4}) +(?P<layer5_cloud_amount>.) +(?P<layer5_height>.{3,4})$')
re_line3ct = re.compile(b'^(?P<scale>.{3}) (?P<measurement_mode>.) (?P<pulse_energy>...) (?P<laser_temperature>...) (?P<receiver_sensitivity>...) (?P<window_contamination>....) (?P<tilt_angle>...) (?P<background_light>.{4}) (?P<pulse_length>.)F(?P<pulse_count>.)(?P<receiver_gain>.)(?P<receiver_bandwidth>.)(?P<sampling>.) (?P<backscatter_sum>...)$')
re_line4 = re.compile(b'^(?P<scale>.{5}) (?P<vertical_resolution>..) (?P<nsamples>.{4}) (?P<pulse_energy>...) (?P<laser_temperature>...) (?P<window_transmission>...) (?P<tilt_angle>..) (?P<background_light>.{4}) (?P<pulse_length>.)(?P<pulse_count>.{4})(?P<receiver_gain>.)(?P<receiver_bandwidth>.)(?P<sampling>..) (?P<backscatter_sum>...)$')
re_line4ct = re.compile(b'^(?P<start_distance>...)(?P<backscatter_segment>.*)$')
re_line5 = re.compile(b'^(?P<backscatter>.*)$')
re_line6 = re.compile(b'^\x03?(?P<checksum>.{4})\x04?$')
re_line20ct = re.compile(b'^\x03$')
re_none = re.compile(b'^/* *$')

re_his_time = re.compile(b'^(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d) (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)$')

def fsencode(x):
    return os.fsencode(x) if sys.version_info[0] > 2 else x

def fsdecode(x):
    return os.fsdecode(x) if sys.version_info[0] > 2 else x

def is_none(s):
    return re_none.match(s)

def int_to_float(x):
    return np.where(x != NA_INT32, x, np.nan)

def read_int(d, g, var):
    d[var] = int(g[var]) if not is_none(g[var]) else NA_INT32

def read_str(d, g, var):
    d[var] = g[var]

def read_hex(d, g, var):
    d[var] = int(g[var], 16)

def read_hex_array(d, g, var, k):
    x = g[var]
    n = len(x)
    d[var] = np.zeros(int(np.ceil(1.0*n/k)), dtype=int)
    for i in range(0, n, k):
        y = x[i:min(i + k, n)]
        z = int(y, 16)
        d[var][int(i/k)] = z if z < (1<<(k*4 - 1)) else z - (1<<(k*4))

def line_time(d, s, filename=None):
    m1 = re_line_time_1.match(s)
    m2 = re_line_time_2.match(s)
    m3 = re_line_time_3.match(s)
    mf = re_file_time.match(filename) if filename is not None else None
    if m1 is not None:
        g = m1.groupdict()
        d['time_utc'] = b'%s-%s-%sT%s:%s:%s' % (
            g['year'],
            g['month'],
            g['day'],
            g['hour'],
            g['minute'],
            g['second']
        )
    elif m2 is not None:
        g = m2.groupdict()
        time = dt.datetime(1970, 1, 1) + \
            dt.timedelta(seconds=float(g['unix_time']))
        d['time_utc'] = time.strftime('%Y-%m-%dT%H:%M:%S').encode('ascii')
    elif m3 is not None and mf is not None:
        g = m3.groupdict()
        gf = mf.groupdict()
        d['time_utc'] = b'20%s-%s-%sT%s:%s:%s' % (
            gf['year'],
            gf['month'],
            gf['day'],
            g['hour'],
            g['minute'],
            g['second']
        )
    else:
        raise ValueError('Invalid syntax for time format')

def line1(d, s):
    m = re_line1.match(s)
    mct = re_line1ct.match(s)
    if m is None and mct is None: raise ValueError('Invalid syntax for "line 1" format')
    if m is None: m = mct
    g = m.groupdict()
    read_str(d, g, 'id')
    read_str(d, g, 'unit')
    read_int(d, g, 'software_level')
    read_int(d, g, 'message_number')
    read_int(d, g, 'message_subclass')

def line2(d, s):
    if d['id'] == b'CT':
        m = re_line2ct.match(s)
    else:
        m = re_line2.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 2" format')
    g = m.groupdict()
    read_str(d, g, 'detection_status')
    read_str(d, g, 'self_check')
    read_int(d, g, 'cbh_or_vertical_visibility')
    read_int(d, g, 'cbh2_or_highest_signal')
    read_int(d, g, 'cbh_3')
    read_hex(d, g, 'status_alarm')
    read_hex(d, g, 'status_warning')
    read_hex(d, g, 'status_internal')

    d['vertical_visibility'] = \
        d['cbh_or_vertical_visibility'] \
        if d['detection_status'] == b'4' \
        else NA_INT32

    d['cbh_1'] = \
        d['cbh_or_vertical_visibility'] \
        if d['detection_status'] in (b'1', b'2', b'3') \
        else NA_INT32

    d['cbh_2'] = \
        d['cbh2_or_highest_signal'] \
        if d['detection_status'] in (b'2', b'3') \
        else NA_INT32

    d['highest_signal'] = \
        d['cbh2_or_highest_signal'] \
        if d['detection_status'] == b'4' \
        else NA_INT32

def line3(d, s):
    m = re_line3.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 3" format')
    g = m.groupdict()
    read_int(d, g, 'sky_detection_status')
    read_int(d, g, 'layer1_height')
    read_int(d, g, 'layer2_cloud_amount')
    read_int(d, g, 'layer2_height')
    read_int(d, g, 'layer3_cloud_amount')
    read_int(d, g, 'layer3_height')
    read_int(d, g, 'layer4_cloud_amount')
    read_int(d, g, 'layer4_height')
    read_int(d, g, 'layer5_cloud_amount')
    read_int(d, g, 'layer5_height')

    d['layer1_cloud_amount'] = \
        d['sky_detection_status'] \
        if d['sky_detection_status'] >= 0 and d['sky_detection_status'] <= 8 \
        else NA_INT32

    if not (
        d['sky_detection_status'] >= 0 and
        d['sky_detection_status'] <= 8
    ):
        d['layer2_cloud_amount'] = NA_INT32
        d['layer3_cloud_amount'] = NA_INT32
        d['layer4_cloud_amount'] = NA_INT32
        d['layer5_cloud_amount'] = NA_INT32

def line3ct(d, s):
    return line4(d, s)

def line4(d, s):
    if d['id'] == b'CT':
        m = re_line3ct.match(s)
        if m is None: raise ValueError('Invalid syntax for "line 3" format')
    else:
        m = re_line4.match(s)
        if m is None: raise ValueError('Invalid syntax for "line 4" format')
    g = m.groupdict()
    read_int(d, g, 'scale')
    read_int(d, g, 'pulse_energy')
    read_int(d, g, 'laser_temperature')
    read_int(d, g, 'tilt_angle')
    read_int(d, g, 'background_light')
    read_str(d, g, 'pulse_length')
    read_int(d, g, 'pulse_count')
    read_str(d, g, 'receiver_gain')
    read_str(d, g, 'receiver_bandwidth')
    read_int(d, g, 'backscatter_sum')
    read_int(d, g, 'sampling')
    if d['id'] == b'CT':
        read_str(d, g, 'measurement_mode')
        read_int(d, g, 'receiver_sensitivity')
        read_int(d, g, 'window_contamination')
    else:
        read_int(d, g, 'vertical_resolution')
        read_int(d, g, 'nsamples')
        read_int(d, g, 'window_transmission')

def line4ct(d, s):
    m = re_line4ct.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 4" format')
    g = m.groupdict()
    read_int(d, g, 'start_distance')
    read_hex_array(d, g, 'backscatter_segment', 4)
    i = d['start_distance']
    j = i + len(d['backscatter_segment'])
    if 'backscatter' not in d:
        d['backscatter'] = np.full(256, np.nan, np.float64)
    if i < 0 or j > len(d['backscatter']):
        raise ValueError('Invalid backscatter start distance (%d ft)' %
            (d['start_distance']*100))
    d['backscatter'][i:j] = d['backscatter_segment']
    del d['start_distance'], d['backscatter_segment']

def line5(d, s):
    m = re_line5.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 5" format')
    g = m.groupdict()
    read_hex_array(d, g, 'backscatter', 5)

def line20ct(d, s):
    m = re_line20ct.match(s)
    if m is None:
        raise ValueError('Invalid syntax for "line 20" format')

def line6(d, s):
    m = re_line6.match(s)
    if m is None:
        raise ValueError('Invalid syntax for "line 6" format')
    g = m.groupdict()
    read_hex(d, g, 'checksum')

def check(d):
    if 'checksum' in d and crc16(d['message']) != d['checksum']:
        raise ValueError('Invalid checksum')

def postprocess(d):
    id_ = d.get('id')

    for var in [
        'backscatter',
        'scale',
        'backscatter_sum',
    ]:
        if var in d: d[var] = int_to_float(d[var])

    d['scale'] = d.get('scale', 10)

    scale_factor = 10000 if id_ == b'CT' else 100000

    if 'backscatter' in d:
        d['backscatter'] = d['backscatter']/scale_factor*(d['scale']/100)

    if 'backscatter_sum' in d:
        d['backscatter_sum'] = d['backscatter_sum']/10000*(d['scale']/100)

    if 'status_internal' in d:
        d['units'] = 'm' if (d['status_internal'] & 0x0080) else 'ft'
        layer_height_factor = 100 if d['units'] == 'ft' else 10

    if 'layer1_height' in d:
        d['layer_height'] = NA_INT32*np.ones(5)
        for i in range(5):
            d['layer_height'][i] = d['layer%d_height' % (i + 1)]
        d['layer_height'] = np.where(
            d['layer_height'] != NA_INT32,
            d['layer_height']*layer_height_factor,
            NA_INT32
        )

    if 'layer1_cloud_amount' in d:
        d['layer_cloud_amount'] = NA_INT32*np.ones(5)
        for i in range(5):
            d['layer_cloud_amount'][i] = d['layer%d_cloud_amount' % (i + 1)]

    if 'units' in d and d['units'] == 'ft':
        for var in [
            'vertical_visibility',
            'layer_height',
            'cbh_1',
            'cbh_2',
            'cbh_3',
        ]:
            if var in d:
                d[var] = np.where(
                    d[var] != NA_INT32,
                    d[var]*0.3048,
                    NA_INT32
                )

    if 'pulse_count' in d:
        d['pulse_count'] = np.where(
            d['pulse_count'] != NA_INT32,
            4**(d['pulse_count'] + 1) if id_ == b'CT' \
                else d['pulse_count']*1024,
            NA_INT32
        )

    if 'sampling' in d:
        if id_ == b'CT':
            d['sampling'] *= 10e6
        else:
            d['sampling'] *= 1e6

    if 'time_utc' in d and 'time' not in d:
        d['time'] = np.nan if d['time_utc'] == '' else (
            dt.datetime.strptime(
                d['time_utc'].decode('ascii'),
                '%Y-%m-%dT%H:%M:%S'
            ) - dt.datetime(1970, 1, 1)
        ).total_seconds()

    if 'time' in d and 'time_utc' not in d:
        d['time_utc'] = '' if np.isnan(d['time']) else (
            dt.datetime(1970, 1, 1) + dt.timedelta(seconds=d['time'])
        ).strftime('%Y-%m-%dT%H:%M:%S').encode('ascii')

    d['time_utc'] = d.get('time_utc', '')
    d['time'] = d.get('time', np.nan)

    if id_ == b'CT':
        d['vertical_resolution'] = 30

def crc16(buf):
    crc = 0xffff
    for i in range(len(buf)):
        crc = crc^(ord(buf[i:(i+1)]) << 8) & 0xffff
        for j in range(8):
            xmask = 0x1021 if (crc & 0x8000) else 0
            crc = (crc<<1) & 0xffff
            crc = (crc^xmask) & 0xffff
    return crc^0xffff;

def read_dat(filename, options={}):
    options = dict({
        'check': False,
    }, **options)

    with open(filename, 'rb') as f:
        d = {}
        dd = []
        stage = 0

        def finalize(d):
            if options['check']: check(d)
            if 'time_utc' not in d and 'time' not in d:
                if len(dd) == 0 and options['time']:
                    d['time'] = options['time']
                elif len(dd) > 0 and \
                    'time' in dd[-1] and \
                    options['sampling_rate']:
                    d['time'] = dd[-1]['time'] + options['sampling_rate']
            postprocess(d)
            if len(dd) > 0 and d['id'] != dd[0]['id']:
                raise ValueError('Mixed ceilometer types in one input file are not supported')
            dd.append(d)

        lines = f.readlines()
        for n, line in enumerate(lines):
            line_number = n + 1
            eof = line_number == len(lines)
            linex = line.rstrip()

            if linex == b'':
                continue

            if linex.startswith(b'-') and not re_line_time_1.match(linex):
                continue

            if linex.startswith(b'=') and not re_line_time_3.match(linex):
                continue

            while True:
                try:
                    if stage == 0:
                        d = {}
                        try: line_time(d, linex, filename)
                        except ValueError:
                            stage = 1
                            continue
                        stage = 1
                    elif stage == 1:
                        line1(d, linex)
                        d['message'] = line[1:]
                        stage = 2
                    elif stage == 2:
                        line2(d, linex)
                        d['message'] += line
                        if d['id'] == b'CT' or d['message_number'] == 2:
                            stage = 3
                        else:
                            stage = 4
                    elif stage == 3:
                        if d['id'] == b'CT':
                            line3ct(d, linex)
                        else:
                            line3(d, linex)
                        d['message'] += line
                        stage = 4
                        substage = 1
                    elif stage == 4:
                        if d['id'] == b'CT':
                            line4ct(d, linex)
                        else:
                            line4(d, linex)
                        d['message'] += line
                        if d['id'] == b'CT' and substage < 16:
                            stage = 4
                            substage += 1
                        else:
                            stage = 5
                    elif stage == 5:
                        if d['id'] == b'CT':
                            line20ct(d, linex)
                        else:
                            line5(d, linex)
                        d['message'] += line
                        if d['id'] == b'CT':
                            finalize(d)
                            stage = 0
                        else:
                            stage = 6
                    elif stage == 6:
                        if re_line6.match(linex):
                            line6(d, linex)
                            d['message'] += line[0:1]
                            if 'time_utc' in d or eof:
                                finalize(d)
                                stage = 0
                            else:
                                stage = 7
                        else:
                            if 'time_utc' in d or eof:
                                finalize(d)
                                stage = 0
                            else:
                                stage = 7
                            continue
                    elif stage == 7:
                        try: line_time(d, linex)
                        except ValueError:
                            finalize(d)
                            stage = 0
                            continue
                        finalize(d)
                        stage = 0
                    else:
                        raise RuntimeError('Invalid decoding stage')
                except Exception as e:
                    t, v, tb = sys.exc_info()
                    log.warning('Error on line %d: %s' % (
                        line_number, e
                    ))
                    log.debug(traceback.format_exc())
                    stage = 0
                break
        return dd

def read_his_time(d, s):
    m = re_his_time.match(s)
    if m is not None:
        g = m.groupdict()
        d['time_utc'] = b'%s-%s-%sT%s:%s:%s' % (
            g['year'],
            g['month'],
            g['day'],
            g['hour'],
            g['minute'],
            g['second']
        )
    else:
        raise ValueError('Invalid syntax for CREATEDATE field')

def read_his_period(d, s):
    try:
        d['period'] = int(s)
    except ValueError:
        raise ValueError('Invalid syntax for PERIOD field')

def read_his_backscatter(d, s):
    read_hex_array(d, {'backscatter': s}, 'backscatter', 5)

def read_his(filename, options={}):
    with open(filename, 'rb') as f:
        dd = []
        header = None
        for n, line in enumerate(f.readlines()):
            line_number = n + 1
            try:
                d = {}
                items = line.split(b',')
                items = [x.strip() for x in items]
                if items[0] == b'History file':
                    continue
                if header is None:
                    header = items
                    continue
                for i, h in enumerate(header):
                    s = items[i] if i < len(items) else b''
                    if h == b'CREATEDATE':
                        read_his_time(d, s)
                    elif h == b'CEILOMETER':
                        d['ceilometer'] = s
                    elif h == b'PERIOD':
                        read_his_period(d, s)
                    elif h == b'BS_PROFILE':
                        read_his_backscatter(d, s)
                postprocess(d)
                dd += [d]
            except Exception as e:
                t, v, tb = sys.exc_info()
                log.warning('Error on line %d: %s' % (
                    line_number, e
                ))
                log.debug(traceback.format_exc())
    return dd

def read(filename, options={}):
    filename_lower = filename.lower()
    if filename_lower.endswith(b'.his'):
        return read_his(filename, options)
    else:
        return read_dat(filename, options)

def write_output(dd, filename):
    n = len(dd)
    id_ = dd[0].get('id')
    vars = list(set(itertools.chain(*[list(d.keys()) for d in dd])))

    if os.path.dirname(filename) != b'' and \
        not os.path.exists(os.path.dirname(filename)):
        raise Exception('%s: No such file or directory' % fsdecode(filename))

    f = Dataset(fsdecode(filename), 'w', format='NETCDF4')
    f.createDimension('time', n)

    if 'backscatter' in vars:
        m = np.max([0] + [len(d['backscatter']) for d in dd])
        f.createDimension('level', m)
        level = np.arange(m)

    has_layers = 'layer_height' in vars or 'layer_cloud_amount' in vars
    if has_layers:
        f.createDimension('layer', 5)
        layer = np.arange(5)

    def write_var(var, dtype, attributes={}):
        if not var in vars: return
        fill_value = NA_NETCDF.get(dtype)
        if dtype == 'SX':
            slen = max([len(d[var]) for d in dd])
            dtype = 'S%d' % slen
        v = f.createVariable(var, dtype, ('time',), fill_value=fill_value)
        v[:] = np.array([d[var] for d in dd])
        v.setncatts(attributes)

    def write_profile(var, dtype, attributes={}):
        if not var in vars: return
        fill_value = NA_NETCDF.get(dtype)
        v = f.createVariable(var, dtype, ('time', 'level'), fill_value=fill_value)
        for i, d in enumerate(dd):
            x = d[var]
            v[i, 0:len(x)] = x
        v.setncatts(attributes)

    def write_layer(var, dtype, attributes={}):
        if not var in vars: return
        fill_value = NA_NETCDF.get(dtype)
        v = f.createVariable(var, dtype, ('time', 'layer'), fill_value=fill_value)
        for i, d in enumerate(dd):
            x = d[var]
            v[i, 0:len(x)] = x
        v.setncatts(attributes)

    def write_dim(var, dtype, x, attributes={}):
        v = f.createVariable(var, dtype, (var,))
        v[:] = x
        v.setncatts(attributes)

    write_var('id', 'S2', {
        'long_name': 'ceilometer identification string',
    })
    write_var('time_utc', 'S19', {
        'long_name': 'time (UTC)',
        'standard_name': 'time',
        'units': 'ISO 8601',
    })
    write_var('time', 'f8', {
        'long_name': 'Time',
        'standard_name': 'time',
        'units': 'seconds since 1970-01-01 00:00:00 UTC',
    })
    if 'backscatter' in vars:
        write_dim('level', 'i4', level, {
            'long_name': 'level number',
        })
    if has_layers:
        write_dim('layer', 'i4', layer, {
            'long_name': 'layer number',
        })
    write_profile('backscatter', 'f4', {
        'long_name': 'attenuated volume backscattering coefficient',
        'units': 'km^-1.sr^-1',
    })
    write_var('unit', 'S1', {
        'long_name': 'unit identification character',
    })
    write_var('software_level', 'i4', {
        'long_name': 'software level',
    })
    write_var('message_number', 'i4', {
        'long_name': 'message number',
        'flag_values': '1, 2',
        'flag_meanings': 'message_without_sky_condition_data message_with_sky_condition_data'
    })
    write_var('message_subclass', 'i4', {
        'long_name': 'message subclass',
    })
    write_var('detection_status', 'S1', {
        'long_name': 'detection status',
        'flag_values': '0, 1, 2, 3, 4, 5, /',
        'flag_meanings': 'no_significant_backscatter one_cloud_base_detected two_cloud_bases_detected three_cloud_bases_detected full_obscuration_determined_but_no_cloud_base_detected some_obscuration_detected_but_determined_to_be_transparent raw_data_input_to_algorithm_missing_or_suspect',
    })
    write_var('self_check', 'S1', {
        'long_name': 'self check',
        'flag_values': '0, W, A',
        'flag_meanings': 'self_check_ok warning_active alarm_active',
    })
    write_var('vertical_visibility', 'i4', {
        'long_name': 'vertical visibility',
        'units': 'm',
    })
    write_var('cbh_1', 'i4', {
        'long_name': 'lowest cloud base height',
        'units': 'm',
    })
    write_var('cbh_2', 'i4', {
        'long_name': 'second lowest cloud base height',
        'units': 'm',
    })
    write_var('cbh_3', 'i4', {
        'long_name': 'highest cloud base height',
        'units': 'm',
    })
    write_var('highest_signal', 'i4', {
        'long_name': 'highest signal detected',
    })
    write_var('status_alarm', 'i4', {
        'long_name': 'status alarm',
        'flag_masks': \
            [0x80, 0x40, 0x20, 0x10] \
            if id_ == b'CT' \
            else [0x8000, 0x4000, 0x2000, 0x1000, 0x0400, 0x0200, 0x0100],
        'flag_meanings': \
            'laser_temperature_shut-off laser_failure receiver_failure voltage_failure'
            if id_ == b'CT' \
            else 'transmitter_shut-off transmitter_failure receiver_failure voltage_failure memory_error light_path_obstruction receiver_saturation',
    })
    write_var('status_warning', 'i4', {
        'long_name': 'status warning',
        'flag_masks': \
            [0x800, 0x400, 0x200, 0x100, 0x080, 0x040, 0x020, 0x010, 0x008] \
            if id_ == b'CT' \
            else [0x8000, 0x4000, 0x2000, 0x1000, 0x0800, 0x0100, 0x0080, 0x0040, 0x0020, 0x0010, 0x0008, 0x0004, 0x0002],
        'flag_meanings': 'window_contamination battery_low laser_power_low laser_temperature_high_or_low internal_temperature_high_or_low voltage_high_or_low relative_humidity_>_85% receiver_optical_cross-talk_compensation_poor blower_suspect' \
            if id_ == b'CT' \
            else 'window_contamination battery_voltage_low transmitter_expires high_humidity blower_failure humidity_sensor_failure heater_fault high_background_radiance ceilometer_engine_board_failure battery_failure laser_monitor_failure receiver_warning tilt_angle_>_45_degrees_warning',
    })
    write_var('status_internal', 'i4', {
        'long_name': 'status internal',
        'flag_masks': \
            [0x800, 0x400, 0x200, 0x100, 0x080, 0x040, 0x020, 0x010, 0x008, 0x004, 0x002] \
            if id_ == b'CT' \
            else [0x8000, 0x4000, 0x2000, 0x1000, 0x0800, 0x0400, 0x0200, 0x0080, 0x0040, 0x0020],
        'flag_meanings': \
            'blower_is_on blower_heater_is_on internal_heater_is_on units_are_meters_if_on_else_feet polling_mode_is_on working_from_battery single_sequence_mode_is_on manual_settings_are_effective tilt_angle_>_45_degrees high_background_radiance manual_blower_control' \
            if id_ == b'CT' \
            else 'blower_is_on blower_heater_is_on internal_heater_is_on working_from_battery standby_mode_is_on self_test_in_progress manual_data_acquisition_settings_are_effective units_are_meters_if_on_else_feet manual_blower_control polling_mode_is_on',
    })
    write_var('vertical_resolution', 'i4', {
        'long_name': 'vertical resolution',
        'units': 'm',
    })
    write_var('sky_detection_status', 'i4', {
        'long_name': 'sky detection status',
        'flag_values': '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 99',
        'flag_meanings': '0_octas 1_octas 2_octas 3_octas 4_octas 5_octas 6_octas 7_octas 8_octas vertical_visibility data_missing not_enough_data',
    })
    write_var('measurement_mode', 'S1', {
        'long_name': 'measurement mode',
        'flag_values': 'N, C',
        'flag_meanings': 'normal close_range'
    })
    write_var('receiver_sensitivity', 'i4', {
        'long_name': 'receiver sensitivity',
        'units': '%',
        'comment': 'percentage of nominal factory setting',
    })
    write_var('window_contamination', 'i4', {
        'long_name': 'window contamination',
        'units': 'millivolt',
        'comment': 'millivolts at internal ADC input',
        'valid_range': [0, 2500],
    })
    write_var('sampling', 'i4', {
        'long_name': 'sampling',
        'units': 'Hz',
    })
    write_var('pulse_energy', 'i4', {
        'long_name': 'pulse energy',
        'units': '%',
        'comment': 'percentage of nominal factory setting',
    })
    write_var('laser_temperature', 'i4', {
        'long_name': 'laser temperature',
        'units': 'degree_Celsius',
    })
    write_var('window_transmission', 'i4', {
        'long_name': 'window transmission estimate',
        'units': '%',
        'comment': '90% to 100% means the window is clean',
    })
    write_var('tilt_angle', 'i4', {
        'long_name': 'tilt angle',
        'units': 'degree',
    })
    write_var('background_light', 'i4', {
        'long_name': 'Background light',
        'units': 'millivolt',
        'comment': 'millivolts at internal ADC input',
        'valid_range': [0, 2500],
    })
    write_var('pulse_length', 'S1', {
        'long_name': 'pulse length',
        'flag_values': 'L, S',
        'flag_meanings': 'long short'
    })
    write_var('pulse_count', 'i4', {
        'long_name': 'pulse count',
        'comment': 'number of pulses during a single measurement cycle',
    })
    write_var('receiver_gain', 'S1', {
        'long_name': 'receiver gain',
        'flag_values': 'H, L',
        'flag_meanings': 'high low',
        'comment': 'high by default, may be low in fog or heavy snow',
    })
    write_var('receiver_bandwidth', 'S1', {
        'long_name': 'Receiver bandwidth',
        'flag_values': 'N, W',
        'flag_meanings': 'narrow wide'
    })
    write_var('backscatter_sum', 'f4', {
        'long_name': 'backscatter sum',
        'units': 'sr^-1',
        'comment': 'sum of detected and normalized backscatter',
    })
    write_var('ceilometer', 'SX', {
        'long_name': 'ceilometer name',
    })
    write_var('period', 'i4', {
        'long_name': 'period',
    })
    write_layer('layer_height', 'i4', {
        'long_name': 'layer height',
        'units': 'm',
        'comment': 'sky condition algorithm',
    })
    write_layer('layer_cloud_amount', 'i4', {
        'long_name': 'layer cloud amount',
        'units': 'octas',
        'comment': 'sky condition algorithm',
    })

    f.software = 'cl2nc (https://github.com/peterkuma/cl2nc)'
    f.version = __version__
    f.created = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    f.close()

def parse_iso_time(s):
    if s is None: return None
    try:
        return (
            dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
            - dt.datetime(1970, 1, 1)
        ).total_seconds()
    except ValueError:
        log.warning('Invalid time format "%s"' % s)

def parse_float(s):
    if s is None: return None
    try:
        return float(s)
    except ValueError:
        log.warning('Invalid floating-point format "%s"' % s)

def main():
    parser = argparse.ArgumentParser(description='Convert Vaisala CL51 and CL31 DAT and HIS L2 files to NetCDF')
    parser.add_argument('-v',
        action='version',
        version='%(prog)s ' +  __version__
    )
    parser.add_argument('-c',
        dest='check',
        action='store_true',
        help='enable DAT checksum verification (slow)'
    )
    parser.add_argument('-q',
        dest='quiet',
        action='store_true',
        help='run quietly (suppress output)'
    )
    parser.add_argument('--debug',
        dest='debug',
        action='store_true',
        help='print debugging information',
    )
    parser.add_argument('-t',
        dest='time',
        help='initial time as <year>-<month>-<day>T<hour>:<minute>:<second> for use with files with no timestamps',
    )
    parser.add_argument('-s',
        dest='sampling_rate',
        help='profile sampling rate in seconds for use with files with no timestamps',
    )
    parser.add_argument('input', help='input file')
    parser.add_argument('output', help='output file')
    args = parser.parse_args()

    if args.debug:
        log.setLevel('DEBUG')

    input_ = fsencode(args.input)
    output = fsencode(args.output)

    options = {
        'check': args.check,
        'time': parse_iso_time(args.time),
        'sampling_rate': parse_float(args.sampling_rate),
    }

    if os.path.isdir(input_):
        for file_ in sorted([fsencode(x) for x in os.listdir(input_)]):
            file_lower = file_.lower()
            if not (file_lower.endswith(b'.dat') or file_lower.endswith(b'.his')):
                continue
            input_filename = os.path.join(input_, file_)
            output_filename = os.path.join(
                output,
                os.path.splitext(file_)[0] + b'.nc'
            )
            if not args.quiet:
                print(fsdecode(input_filename))
            try:
                dd = read(input_filename, options)
                if len(dd) > 0:
                    write_output(dd, output_filename)
                else:
                    log.warning('No output was created because the input file has no records')
            except Exception as e:
                log.error(e)
                log.debug(traceback.format_exc())
    else:
        try:
            dd = read(input_, options)
            if len(dd) > 0:
                write_output(dd, output)
            else:
                log.warning('No output was created because the input file has no records')
        except Exception as e:
            log.error(e)
            log.debug(traceback.format_exc())

if __name__ == '__main__':
    main()
