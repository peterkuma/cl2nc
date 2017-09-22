# cl2nc

cl2nc is a command-line Python program for converting
Vaisala CL51 and CL31 dat files to NetCDF.

## Example

    cl2nc input.dat output.nc
    cl2nc input.dat output.nc

## Install

Requirements:

- Python 2.7

To install with the Python package manager on Linux:

    pip install cl2nc

From source:

    pip install python-netcdf4
    python setup.py install

## Usage

### cl2nc

    cl2nc <input> <output>

- `input` - input dat file
- `output` - output HDF file

## Variables

Please see Vaisala CL51 User's Guide for a complete description of the
variables.

### background_light

Background light (mV)

Millivolts at internal ADC input.

### backscatter

Attenuated volume backscatter coefficient (km-^1.sr^-1)

### backscatter_sum

Backscatter sum (sr^-1)

Sum of detected and normalized backscatter (0-0.0999 sr^-1).

### bandwidth

Bandwidth

- `N` - narrow
- `W` - wide

Narrow by default.

### detection_status

Detection status

- `0` - no significant backscatter
- `1` - one cloud base detected
- `2` - two cloud bases detected
- `3` - three cloud bases detected
- `4` - full obscuration determined but no cloud base detected
- `5` - some obscuration detected but determined to be transparent
- `/` - raw data input to algorithm missing or suspect

### sky_detection_status

Sky detection status

- 0-8 - cloud coverage of the first layer in octas
- 9 - vertical visibility
- -1 - data missing, sky condition option not active or ceilometer in standby mode
- 99 - not enough data (after start-up)

### gain

Gain

- `H` - high
- `L` - low

High by default, may be low in fog or heavy snow.

### height

Height (m)

### highest_cbh

Highest cloud base height (m)

### highest_signal

Highest signal detected

### laser_temperature

Laser temperature (C)

### layer_cloud_amount

Layer cloud amount (octas)

### layer_height

Layer height (m)

### level

Level

### lowest_cbh

Lowest cloud base height (m)

### message_number

Message number

- 1 - message without sky condition data
- 2 - message with sky condition data

### pulse_energy

Pulse Energy (% of nominal factory setting)

### pulse_length

Pulse length

- `L` - long (100 ns)
- `S` - short

### pulse_qty

Pulse qty

### second_lowest_cbh

Second lowest cloud base height (m)

### self_check

Self check

- `0` - self-check OK
- `W` - at least one warning active, no alarms
- `A` - at least one alarm active

### software_level

Software level ID

### status_alarm

Status alarm

Flags:

- 0x8000 - transmitter shut-off
- 0x4000 - transmitter failure
- 0x2000 - receiver failure
- 0x1000 - voltage failure
- 0x0400 - memory error
- 0x0200 - light path obstruction
- 0x0100 - receiver saturation

### status_internal

Status internal

Flags:

- 0x8000 - blower is on
- 0x4000 - blower heater is on
- 0x2000 - internal heater is on
- 0x1000 - working from battery
- 0x0800 - standby mode is on
- 0x0400 - self test in progress
- 0x0200 - manual data acquisition settings are effective
- 0x0080 - units are meters if on, else feet (note that units are always converted to m by cl2nc)
- 0x0040 - manual blower control
- 0x0020 - polling mode is on

### status_warning

Status warning

Flags:

- 0x8000 - window contamination
- 0x4000 - battery voltage low
- 0x2000 - transmitter expires
- 0x1000 - high humidity
- 0x0800 - blower failure
- 0x0100 - humidity sensor failure
- 0x0080 - heater fault
- 0x0040 - high background radiance
- 0x0020 - ceilometer engine board failure
- 0x0010 - battery failure
- 0x0008 - laser monitor failure
- 0x0004 - receiver warning
- 0x0002 - tilt angle > 45 degrees warning

### subclass

Message subclass

- 6 - 10 m x 1540 samples, range 15400 m (msg1_10x1540)
- 8 - without a backscatter profile (msg1_base)

### tilt_angle

Tilt angle (degrees from vertical)

### time

Time (ISO 8601)

### unit

Unit identification character

### vertical_resolution

Vertical resolution (m)

### vertical_visibility

Vertical visibility

### window_transmission

Window transmission estimate (%)

The estimated transparency of 90% to 100% means that the window is clean.

## License

MIT License (see [LICENSE.md](LICENSE.md))
