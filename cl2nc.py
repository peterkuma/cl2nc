#!/usr/bin/env python

__version__ = '3.2.2'

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
NA_FLOAT32 = np.nan
NA_FLOAT64 = np.nan

NA_NETCDF = {
    'i4': NA_INT32,
    'i8': NA_INT64,
    'f4': NA_FLOAT32,
    'f8': NA_FLOAT64,
}

re_line0 = re.compile(b'^-(?P<year>\d{4})-(?P<month>\d\d)-(?P<day>\d\d) (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)$')
re_line0x = re.compile(b'^(?P<unix_time>\d*\.?\d*)$')
re_line1 = re.compile(b'^\x01CL(?P<unit>.)(?P<software_level>\d\d\d)(?P<message_number>\d)(?P<message_subclass>\d)\x02?$')
re_line2 = re.compile(b'^(?P<detection_status>.)(?P<self_check>.) (?P<cbh_or_vertical_visibility>.{5}) (?P<cbh2_or_highest_signal>.{5}) (?P<cbh_3>.{5}) (?P<status_alarm>.{4})(?P<status_warning>.{4})(?P<status_internal>.{4})$')
re_line3 = re.compile(b'^ (?P<sky_detection_status>..) +(?P<layer1_height>.{4}) +(?P<layer2_cloud_amount>.) +(?P<layer2_height>.{4}) +(?P<layer3_cloud_amount>.) +(?P<layer3_height>.{4}) +(?P<layer4_cloud_amount>.) +(?P<layer4_height>.{4}) +(?P<layer5_cloud_amount>.) +(?P<layer5_height>.{3,4})$')
re_line4 = re.compile(b'^(?P<scale>.{5}) (?P<vertical_resolution>..) (?P<nsamples>.{4}) (?P<pulse_energy>...) (?P<laser_temperature>...) (?P<window_transmission>...) (?P<tilt_angle>..) (?P<background_light>.{4}) (?P<pulse_length>.)(?P<pulse_count>.{4})(?P<receiver_gain>.)(?P<receiver_bandwidth>.)(?P<sampling>..) (?P<backscatter_sum>...)$')
re_line5 = re.compile(b'^(?P<backscatter>.*)$')
re_line6 = re.compile(b'^\x03(?P<checksum>.{4})\x04$')
re_line6x = re.compile(b'^(?P<time_utc>\d+)$')
re_none = re.compile(b'^/* *$')

def fsencode(x):
    return os.fsencode(x) if sys.version_info[0] > 2 else x

def fsdecode(x):
    return os.fsdecode(x) if sys.version_info[0] > 2 else x

def is_none(s):
    return re_none.match(s)

def int_to_float(x):
    return np.where(x != NA_INT32, x, np.nan)

def read_int(d, d2, var):
    d2[var] = int(d[var]) if not is_none(d[var]) else NA_INT32

def read_str(d, d2, var):
    d2[var] = d[var]

def read_hex(d, d2, var):
    d2[var] = int(d[var], 16)

def read_hex_array(d, d2, var, k):
    x = d[var]
    n = len(x)
    d2[var] = np.zeros(int(np.ceil(1.0*n/k)), dtype=int)
    for i in range(0, n, k):
        y = x[i:min(i + k, n)]
        z = int(y, 16)
        d2[var][int(i/k)] = z if z < (1<<(k*4 - 1)) else z - (1<<(k*4))

def line0(s):
    m = re_line0.match(s)
    if m is None: raise ValueError('Invalid syntax for time format')
    d = m.groupdict()
    d2 = {}
    d2['time_utc'] = b'%s-%s-%sT%s:%s:%s' % (
        d['year'],
        d['month'],
        d['day'],
        d['hour'],
        d['minute'],
        d['second']
    )
    return d2

def line0x(s):
    m = re_line0x.match(s)
    if m is None: raise ValueError('Invalid syntax for time format')
    d = m.groupdict()
    d2 = {}
    time = dt.datetime(1970,1,1) + dt.timedelta(seconds=float(d['unix_time']))
    d2['time_utc'] = time.strftime(u'%Y-%m-%dT%H:%M:%S').encode('ascii')
    return d2

def line1(s):
    m = re_line1.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 1" format')
    d = m.groupdict()
    d2 = {}
    read_str(d, d2, 'unit')
    read_int(d, d2, 'software_level')
    read_int(d, d2, 'message_number')
    read_int(d, d2, 'message_subclass')
    return d2

def line2(s):
    m = re_line2.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 2" format')
    d = m.groupdict()
    d2 = {}
    read_str(d, d2, 'detection_status')
    read_str(d, d2, 'self_check')
    read_int(d, d2, 'cbh_or_vertical_visibility')
    read_int(d, d2, 'cbh2_or_highest_signal')
    read_int(d, d2, 'cbh_3')
    read_hex(d, d2, 'status_alarm')
    read_hex(d, d2, 'status_warning')
    read_hex(d, d2, 'status_internal')

    d2['vertical_visibility'] = \
        d2['cbh_or_vertical_visibility'] \
        if d2['detection_status'] == b'4' \
        else NA_INT32

    d2['cbh_1'] = \
        d2['cbh_or_vertical_visibility'] \
        if d2['detection_status'] in (b'1', b'2', b'3') \
        else NA_INT32

    d2['cbh_2'] = \
        d2['cbh2_or_highest_signal'] \
        if d2['detection_status'] in (b'2', b'3') \
        else NA_INT32

    d2['highest_signal'] = \
        d2['cbh2_or_highest_signal'] \
        if d2['detection_status'] == b'4' \
        else NA_INT32

    return d2

def line3(s):
    m = re_line3.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 3" format')
    d = m.groupdict()
    d2 = {}
    read_int(d, d2, 'sky_detection_status')
    read_int(d, d2, 'layer1_height')
    read_int(d, d2, 'layer2_cloud_amount')
    read_int(d, d2, 'layer2_height')
    read_int(d, d2, 'layer3_cloud_amount')
    read_int(d, d2, 'layer3_height')
    read_int(d, d2, 'layer4_cloud_amount')
    read_int(d, d2, 'layer4_height')
    read_int(d, d2, 'layer5_cloud_amount')
    read_int(d, d2, 'layer5_height')

    d2['layer1_cloud_amount'] = \
        d2['sky_detection_status'] \
        if d2['sky_detection_status'] >= 0 and d2['sky_detection_status'] <= 8 \
        else NA_INT32

    if not (
        d2['sky_detection_status'] >= 0 and
        d2['sky_detection_status'] <= 8
    ):
        d2['layer2_cloud_amount'] = NA_INT32
        d2['layer3_cloud_amount'] = NA_INT32
        d2['layer4_cloud_amount'] = NA_INT32
        d2['layer5_cloud_amount'] = NA_INT32

    return d2

def line4(s):
    m = re_line4.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 4" format')
    d = m.groupdict()
    d2 = {}
    read_int(d, d2, 'scale')
    read_int(d, d2, 'vertical_resolution')
    read_int(d, d2, 'nsamples')
    read_int(d, d2, 'pulse_energy')
    read_int(d, d2, 'laser_temperature')
    read_int(d, d2, 'window_transmission')
    read_int(d, d2, 'tilt_angle')
    read_int(d, d2, 'background_light')
    read_str(d, d2, 'pulse_length')
    read_int(d, d2, 'pulse_count')
    read_str(d, d2, 'receiver_gain')
    read_str(d, d2, 'receiver_bandwidth')
    read_int(d, d2, 'backscatter_sum')
    return d2

def line5(s):
    m = re_line5.match(s)
    if m is None: raise ValueError('Invalid syntax for "line 5" format')
    d = m.groupdict()
    d2 = {}
    read_hex_array(d, d2, 'backscatter', 5)
    return d2

def line6(s):
    m = re_line6.match(s)
    if m is None:
        raise ValueError('Invalid syntax for "line 6" format')
    d = m.groupdict()
    d2 = {}
    read_hex(d, d2, 'checksum')
    return d2

def line6x(s):
    m = re_line6x.match(s)
    if m is None:
        raise ValueError('Invalid syntax for "line 6" format')
    d = m.groupdict()
    d2 = {}
    read_int(d, d2, 'time_utc')
    d2['time_utc'] = (
        dt.datetime(1970, 1, 1) +
        dt.timedelta(0, d2['time_utc'])
    ).strftime(b'%Y-%m-%dT%H:%M:%S')
    return d2

def check(d):
    if 'checksum' in d and crc16(d['message']) != d['checksum']:
        raise ValueError('Invalid checksum')

def postprocess(d):
    for var in [
        'backscatter',
        'scale',
        'backscatter_sum',
    ]:
        d[var] = int_to_float(d[var])

    d['backscatter'] = d['backscatter']/100000.0*(d['scale']/100.0)
    d['backscatter_sum'] = d['backscatter_sum']/10000.0*(d['scale']/100.0)

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

    if d['units'] == 'ft':
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

    d['pulse_count'] = np.where(
        d['pulse_count'] != NA_INT32,
        d['pulse_count']*1024,
        NA_INT32
    )

    d['time_utc'] = d.get('time_utc', '')
    d['time'] = NA_INT64 if d['time_utc'] == '' else (
        dt.datetime.strptime(d['time_utc'].decode('ascii'), '%Y-%m-%dT%H:%M:%S')
        - dt.datetime(1970, 1, 1)
    ).total_seconds()

def crc16(buf):
    crc = 0xffff
    for i in range(len(buf)):
        crc = crc^(ord(buf[i:(i+1)]) << 8) & 0xffff
        for j in range(8):
            xmask = 0x1021 if (crc & 0x8000) else 0
            crc = (crc<<1) & 0xffff
            crc = (crc^xmask) & 0xffff
    return crc^0xffff;

def read_input(filename, options={}):
    options = dict({
        'check': False,
    }, **options)

    with open(filename, 'rb') as f:
        d = {}
        dd = []
        stage = 0
        line_number = 0

        for line in f.readlines():
            line_number += 1
            linex = line.rstrip()

            if linex == b'':
                continue

            if linex.startswith(b'-') and not re_line0.match(linex):
                continue

            while True:
                try:
                    if stage == 0:
                        d = {}
                        if re_line0.match(linex):
                            d.update(line0(linex))
                        elif re_line0x.match(linex):
                            d.update(line0x(linex))
                        stage = 1
                    elif stage == 1:
                        d.update(line1(linex))
                        d['message'] = line[1:]
                        stage = 2
                    elif stage == 2:
                        d.update(line2(linex))
                        d['message'] += line
                        if d['message_number'] == 2:
                            stage = 3
                        else:
                            stage = 4
                    elif stage == 3:
                        d.update(line3(linex))
                        d['message'] += line
                        stage = 4
                    elif stage == 4:
                        d.update(line4(linex))
                        d['message'] += line
                        stage = 5
                    elif stage == 5:
                        d.update(line5(linex))
                        d['message'] += line
                        stage = 6
                    elif stage == 6:
                        try:
                            d.update(line6(linex))
                            d['message'] += line[0:1]
                        except:
                            d.update(line6x(linex))
                        if options['check']: check(d)
                        postprocess(d)
                        dd.append(d)
                        stage = 0
                    else:
                        raise RuntimeError('Invalid decoding stage')
                except Exception as e:
                    t, v, tb = sys.exc_info()
                    log.error('Error on line %d: %s' % (
                        line_number, e
                    ))
                    log.debug(traceback.format_exc())
                    return []
                break
        return dd

def write_output(dd, filename):
    n = len(dd)
    vars = list(set(itertools.chain(*[list(d.keys()) for d in dd])))
    m = np.max([0] + [len(d['backscatter']) for d in dd])

    if os.path.dirname(filename) != b'' and \
        not os.path.exists(os.path.dirname(filename)):
        raise Exception('%s: No such file or directory' % fsdecode(filename))

    f = Dataset(fsdecode(filename), 'w', format='NETCDF4')
    f.createDimension('time', n)
    f.createDimension('level', m)
    f.createDimension('layer', 5)
    level = np.arange(m)
    layer = np.arange(5)

    def write_var(var, dtype, attributes={}):
        if not var in vars: return
        fill_value = NA_NETCDF.get(dtype)
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

    write_var('time_utc', 'S19', {
        'long_name': 'Time (UTC)',
        'units': 'ISO 8601',
    })
    write_var('time', 'i8', {
        'long_name': 'Time',
        'units': 'seconds since 1970-01-01 00:00:00 UTC',
    })
    write_dim('level', 'i4', level, {
        'long_name': 'Level number',
    })
    write_dim('layer', 'i4', layer, {
        'long_name': 'Layer number',
    })
    write_profile('backscatter', 'f4', {
        'long_name': 'Attenuated volume backscatter coefficient',
        'units': 'km^-1.sr^-1',
    })
    write_var('unit', 'S1', {
        'long_name': 'Unit identification character',
    })
    write_var('software_level', 'i4', {
        'long_name': 'Software level',
    })
    write_var('message_number', 'i4', {
        'long_name': 'Message number',
        'flag_values': '1, 2',
        'flag_meanings': 'message_without_sky_condition_data message_with_sky_condition_data'
    })
    write_var('message_subclass', 'i4', {
        'long_name': 'Message subclass',
    })
    write_var('detection_status', 'S1', {
        'long_name': 'Detection status',
        'flag_values': '0, 1, 2, 3, 4, 5, /',
        'flag_meanings': 'no_significant_backscatter one_cloud_base_detected two_cloud_bases_detected three_cloud_bases_detected full_obscuration_determined_but_no_cloud_base_detected some_obscuration_detected_but_determined_to_be_transparent raw_data_input_to_algorithm_missing_or_suspect',
    })
    write_var('self_check', 'S1', {
        'long_name': 'Self check',
        'flag_values': '0, W, A',
        'flag_meanings': 'self_check_ok warning_active alarm_active',
    })
    write_var('vertical_visibility', 'i4', {
        'long_name': 'Vertical visibility',
        'units': 'm',
    })
    write_var('cbh_1', 'i4', {
        'long_name': 'Lowest cloud base height',
        'units': 'm',
    })
    write_var('cbh_2', 'i4', {
        'long_name': 'Second lowest cloud base height',
        'units': 'm',
    })
    write_var('cbh_3', 'i4', {
        'long_name': 'Highest cloud base height',
        'units': 'm',
    })
    write_var('highest_signal', 'i4', {
        'long_name': 'Highest signal detected',
    })
    write_var('status_alarm', 'i4', {
        'long_name': 'Status alarm',
    })
    write_var('status_warning', 'i4', {
        'long_name': 'Status warning',
        'units': 'degree_Celsius',
    })
    write_var('status_internal', 'i4', {
        'long_name': 'Status internal',
    })
    write_var('vertical_resolution', 'i4', {
        'long_name': 'Vertical resolution',
        'units': 'm',
    })
    write_var('sky_detection_status', 'i4', {
        'long_name': 'Sky detection status',
        'flag_values': '0, 1, 2, 3, 4, 5, 6, 7, 8, 9, -1, 99',
        'flag_meanings': '0_octas 1_octas 2_octas 3_octas 4_octas 5_octas 6_octas 7_octas 8_octas vertical_visibility data_missing not_enough_data',
        'comment': 'Sky detection algorithm',
    })
    write_var('pulse_energy', 'i4', {
        'long_name': 'Pulse energy',
        'units': 'percent',
        'comment': 'Percentage of nominal factory setting',
    })
    write_var('laser_temperature', 'i4', {
        'long_name': 'Laser temperature',
        'units': 'degree_Celsius',
    })
    write_var('window_transmission', 'i4', {
        'long_name': 'Window transmission estimate',
        'units': 'percent',
        'comment': '90% to 100% means the window is clean',
    })
    write_var('tilt_angle', 'i4', {
        'long_name': 'Tilt angle',
        'units': 'degrees',
    })
    write_var('background_light', 'i4', {
        'long_name': 'Background light',
        'units': 'millivolt',
        'comment': 'Millivolts at internal ADC input',
    })
    write_var('pulse_length', 'S1', {
        'long_name': 'Pulse length',
        'flag_names': 'L, S',
        'flag_meanings': 'long short'
    })
    write_var('pulse_count', 'i4', {
        'long_name': 'Pulse count',
        'comment': 'Number of pulses during a single measurement cycle',
    })
    write_var('receiver_gain', 'S1', {
        'long_name': 'Receiver gain',
        'flag_values': 'H, L',
        'flag_meanings': 'high low',
        'comment': 'High by default, may be low in fog or heavy snow',
    })
    write_var('receiver_bandwidth', 'S1', {
        'long_name': 'Receiver bandwidth',
        'flag_values': 'N, W',
        'flag_meanings': 'narrow wide'
    })
    write_var('backscatter_sum', 'f4', {
        'long_name': 'Backscatter sum',
        'units': 'sr^-1',
        'comment': 'Sum of detected and normalized backscatter',
    })
    write_layer('layer_height', 'i4', {
        'long_name': 'Layer height',
        'units': 'm',
        'comment': 'Sky condition algorithm',
    })
    write_layer('layer_cloud_amount', 'i4', {
        'long_name': 'Layer cloud amount',
        'units': 'octas',
        'comment': 'Sky condition algorithm',
    })

    f.software = 'cl2nc (https://github.com/peterkuma/cl2nc)'
    f.version = __version__
    f.created = dt.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    f.close()

def main():
    parser = argparse.ArgumentParser(description='Convert Vaisala CL51 and CL31 dat files to NetCDF')
    parser.add_argument('-c',
        dest='check',
        action='store_true',
        help='enable checksum verification (slow)'
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
    parser.add_argument('input', help='input file')
    parser.add_argument('output', help='output file')
    args = parser.parse_args()

    if args.debug:
        log.setLevel('DEBUG')
    
    input_ = fsencode(args.input)
    output = fsencode(args.output)

    if os.path.isdir(input_):
        for file_ in sorted([fsencode(x) for x in os.listdir(input_)]):
            if not (file_.endswith(b'.dat') or file_.endswith(b'.DAT')):
                continue
            input_filename = os.path.join(input_, file_)
            output_filename = os.path.join(
                output,
                os.path.splitext(file_)[0] + b'.nc'
            )
            if not args.quiet:
                print(fsdecode(input_filename))
            try:
                dd = read_input(input_filename, {'check': args.check})
                if len(dd) > 0:
                    write_output(dd, output_filename)
            except Exception as e:
                log.error(e)
                log.debug(traceback.format_exc())
    else:
        try:
            dd = read_input(input_, {'check': args.check})
            if len(dd) > 0:
                write_output(dd, output)
        except Exception as e:
            log.error(e)
            log.debug(traceback.format_exc())

if __name__ == '__main__':
    main()
