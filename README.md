# cl2nc

cl2nc is a command-line Python program for converting Vaisala CL51 and CL31 dat
files to NetCDF.

## Example

On the command-line:

    cl2nc input.dat output.nc

where `input.dat` is a Vaisala CL51 or CL31 dat file and `output.nc` is the name
of a NetCDF output file.

## Install

Requirements:

- Python 2.7

To install with the Python package manager on Linux:

    pip install cl2nc

From source:

    pip install netCDF4
    python setup.py install

You can also use the Python script `cl2nc` directly without installation.

**Note:** Alternatively, the package netCDF4 is also present as the package
`python-netcdf` on Debian-based Linux distributions, which you can install with
`apt-get install python-netcdf`.

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

### cbh_1

Lowest cloud base height (m)

### cbh_2

Second lowest cloud base height (m)

### cbh_3

Highest cloud base height (m)

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

### highest_signal

Highest signal detected

### laser_temperature

Laser temperature (C)

### layer

Layer number

### layer_cloud_amount

Layer cloud amount (octas)

Sky condition algorithm.

### layer_height

Layer height (m)

Sky condition algorithm.

### level

Level number

### message_number

Message number

- 1 - message without sky condition data
- 2 - message with sky condition data

### message_subclass

Message subclass

- 6 - 10 m x 1540 samples, range 15400 m (msg1_10x1540)
- 8 - without a backscatter profile (msg1_base)

### pulse_energy

Pulse energy (% of nominal factory setting)

### pulse_length

Pulse length

- `L` - long (100 ns)
- `S` - short

### pulse_count

Pulse count

### receiver_bandwidth

Receiver bandwidth

- `N` - narrow
- `W` - wide

### receiver_gain

Receiver gain

- `H` - high
- `L` - low

High by default, may be low in fog or heavy snow.

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

### tilt_angle

Tilt angle (degrees from vertical)

### time

Time (ISO 8601)

### unit

Unit identification character

### vertical_resolution

Vertical resolution (m)

### vertical_visibility

Vertical visibility (m)

### window_transmission

Window transmission estimate (%)

90% to 100% means the window is clean.

## License

MIT License (see [LICENSE.md](LICENSE.md))

## Contact

Peter Kuma <<peter.kuma@fastmail.com>>
