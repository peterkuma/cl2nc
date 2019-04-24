# cl2nc

cl2nc is an open source command line Python program for converting Vaisala
CL51 and CL31 ceilometer dat files to NetCDF.

## Example

On the command-line:

```sh
cl2nc input.dat output.nc
```

where `input.dat` is a Vaisala CL51 or CL31 dat file and `output.nc` is the name
of a NetCDF output file.

See [example.zip](example.zip) for an example input and output.

## Installation

Supported operating systems:

- Linux
- Windows
- macOS

Requirements:

- Python 2.7

**Note:** Python 3 is currently not supported.

On Windows and macOS [Anaconda/Python 2.7](https://www.anaconda.com/download/)
distribution of Python is recommended. On Linux, use Python 2.7 which comes
with your Linux distribution (either built-in, or installed through a
package manager).

The following commands should be run in the **Terminal** (Linux and macOS)
or **Anaconda Prompt** (Windows – you can find Anaconda Prompt in the
Start menu).

To install from the
[Python Package Index (PyPI)](https://pypi.python.org/pypi/cl2nc):

```sh
pip install cl2nc
```

or to install in the user's home directory
(make sure `~/.local/bin` is in the `PATH` environment variable):

```sh
pip install cl2nc --user
```

Alternatively, to install from source, download and unpack the latest
[cl2nc](https://github.com/peterkuma/cl2nc/archive/master.zip) archive, or
clone the repository from GitHub
(`git clone https://github.com/peterkuma/cl2nc.git`). In the package
directory, run the following commands:

```sh
pip install netCDF4
python setup.py install

# or to install in the user's home directory
# (make sure `~/.local/bin` is in the `PATH` environment variable):

python setup.py install --user
```

You can also use the Python script `cl2nc` directly without installation
(as long as netCDF4 is installed).

Once installed, you should be able to run `cl2nc` in the Terminal
(Linux and macOS) or Anaconda Prompt (Windows).

## Usage

```sh
cl2nc [-c] <input> <output>
```

- `input` – input dat file
- `output` – output NetCDF file
- `-c` – enable checksum verification (slow)

## Variables

Please see Vaisala CL51 User's Guide for a complete description of the
variables.

The DAT files can alternatively contain values in feet
(instead of meters), in which case all values are converted by cl2nc to meters.

Time in DAT files is assumed to be UTC.

Missing values are encoded as NaN (floating-point variables) or -2147483648
(integer variables). The `_FillValue` attribute contains the missing value
used in the given variable.

| Variable | Description | Units | Dimensions |
| --- | --- | --- | --- |
| [background_light](#background_light) | Background light | mV | time |
| [backscatter](#backscatter) | Attenuated volume backscatter coefficient | km<sup>-1</sup>.sr<sup>-1</sup> | time, level |
| [backscatter_sum](#backscatter_sum) | Backscatter sum | sr<sup>-1</sup> | time |
| [cbh_1](#cbh_1) | Lowest cloud base height | m | time |
| [cbh_2](#cbh_2) | Second lowest cloud base height | m | time |
| [cbh_3](#cbh_3) | Highest cloud base height | m | time |
| [detection_status](#detection_status) | Detection status | | time |
| [sky_detection_status](#sky_detection_status) | Sky detection status | | time |
| [highest_signal](#highest_signal) | Highest signal detected | | time |
| [laser_temperature](#laser_temperature) | Laser temperature | °C | time |
| [layer](#layer) | Layer number | | layer |
| [layer_cloud_amount](#layer_cloud_amount) | Layer cloud amount | octas | time, layer |
| [layer_height](#layer_height) | Layer height | m | time, layer |
| [level](#level) | Level number | | level |
| [message_number](#message_number) | Message number | | time |
| [message_subclass](#message_subclass) | Message subclass | | time |
| [pulse_energy](#pulse_energy) | Pulse energy | % | time |
| [pulse_length](#pulse_length) | Pulse length | | time |
| [pulse_count](#pulse_count) | Pulse count | | time |
| [receiver_bandwidth](#receiver_bandwidth) | Receiver bandwidth | | time |
| [receiver_gain](#receiver_gain) | Receiver gain | | time |
| [self_check](#self_check) | Self check | | time |
| [software_level](#software_level) | Software level ID | | time |
| [status_alarm](#status_alarm) | Status alarm | | time |
| [status_internal](#status_internal) | Status internal | | time |
| [status_warning](#status_warning) | Status warning | | time |
| [tilt_angle](#tilt_angle) | Tilt angle | degrees | time |
| [time](#time) | Time | seconds since 1970-01-01 00:00:00 UTC | time |
| [time_utc](#time_utc) | Time (UTC) | ISO 8601 | time |
| [unit](#unit) | Unit identification character | | time |
| [vertical_resolution](#vertical_resolution) | Vertical resolution | m | time |
| [vertical_visibility](#vertical_visibility) | Vertical visibility | m | time |
| [window_transmission](#window_transmission) | Window transmission estimate | % | time |

### background_light

Background light (mV)

Millivolts at internal ADC input.

### backscatter

Attenuated volume backscatter coefficient (km<sup>-1</sup>.sr<sup>-1</sup>)

### backscatter_sum

Backscatter sum (sr<sup>-1</sup>)

Sum of detected and normalized backscatter (0–0.0999 sr<sup>-1</sup>).

### cbh_1

Lowest cloud base height (m)

### cbh_2

Second lowest cloud base height (m)

### cbh_3

Highest cloud base height (m)

### detection_status

Detection status

- `0` – no significant backscatter
- `1` – one cloud base detected
- `2` – two cloud bases detected
- `3` – three cloud bases detected
- `4` – full obscuration determined but no cloud base detected
- `5` – some obscuration detected but determined to be transparent
- `/` – raw data input to algorithm missing or suspect

### sky_detection_status

Sky detection status

- 0-8 – cloud coverage of the first layer in octas
- 9 – vertical visibility
- -1 – data missing, sky condition option not active or ceilometer in standby mode
- 99 – not enough data (after start-up)

### highest_signal

Highest signal detected

### laser_temperature

Laser temperature (°C)

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

- 1 – message without sky condition data
- 2 – message with sky condition data

### message_subclass

Message subclass

- 6 – 10 m ⨉ 1540 samples, range 15400 m (msg1_10x1540)
- 8 – without a backscatter profile (msg1_base)

### pulse_energy

Pulse energy (% of nominal factory setting)

### pulse_length

Pulse length

- `L` – long (100 ns)
- `S` – short

### pulse_count

Pulse count

### receiver_bandwidth

Receiver bandwidth

- `N` – narrow
- `W` – wide

### receiver_gain

Receiver gain

- `H` – high
- `L` – low

High by default, may be low in fog or heavy snow.

### self_check

Self check

- `0` – self-check OK
- `W` – at least one warning active, no alarms
- `A` – at least one alarm active

### software_level

Software level ID

### status_alarm

Status alarm

Flags:

- 0x8000 – transmitter shut-off
- 0x4000 – transmitter failure
- 0x2000 – receiver failure
- 0x1000 – voltage failure
- 0x0400 – memory error
- 0x0200 – light path obstruction
- 0x0100 – receiver saturation

### status_internal

Status internal

Flags:

- 0x8000 – blower is on
- 0x4000 – blower heater is on
- 0x2000 – internal heater is on
- 0x1000 – working from battery
- 0x0800 – standby mode is on
- 0x0400 – self test in progress
- 0x0200 – manual data acquisition settings are effective
- 0x0080 – units are meters if on, else feet (note that units are always converted to m by cl2nc)
- 0x0040 – manual blower control
- 0x0020 – polling mode is on

### status_warning

Status warning

Flags:

- 0x8000 – window contamination
- 0x4000 – battery voltage low
- 0x2000 – transmitter expires
- 0x1000 – high humidity
- 0x0800 – blower failure
- 0x0100 – humidity sensor failure
- 0x0080 – heater fault
- 0x0040 – high background radiance
- 0x0020 – ceilometer engine board failure
- 0x0010 – battery failure
- 0x0008 – laser monitor failure
- 0x0004 – receiver warning
- 0x0002 – tilt angle > 45 degrees warning

### tilt_angle

Tilt angle (degrees from vertical)

### time

Time (seconds since 1970-01-01 00:00:00 UTC, excluding leap seconds)

### time_utc

Time (UTC) (ISO 8601)

### unit

Unit identification character

### vertical_resolution

Vertical resolution (m)

### vertical_visibility

Vertical visibility (m)

### window_transmission

Window transmission estimate (%)

90% to 100% means the window is clean.

## Attributes

### software

cl2nc identification: `cl2nc (https://github.com/peterkuma/cl2nc)`.

### version

cl2nc version string. Follows [semantic versioning](http://semver.org/).

### created

Time when the NetCDF file was created (ISO 8601 UTC).

## License

This software is open source and can be used, shared and modified freely
under the terms of the MIT License (see [LICENSE.md](LICENSE.md)).

## Support

cl2nc has not yet been extensively tested. If you have any doubts about
the output, please check against values in the DAT file or send me the file.

Peter Kuma <<peter.kuma@fastmail.com>>

## FAQ

### cl2nc fails with an exception.

Please make sure you are using Python 2.7 and not Python 3, and you
have the Python package netCDF4 installed. If it still does not work
for you contact me: Peter Kuma <<peter.kuma@fastmail.com>>.

### Where is the height information?

Height can be determined from [vertical_resolution](#vertical_resolution).
The instrument samples vertical bins on regular intervals.

### MATLAB cannot read the time_utc variable.

MATLAB NetCDF implementation currently does not support reading NC_STRING
variables. You can use the `time` variable instead or use the MATLAB HDF
functions to read the file (you may need to change the file extension to `.h5`).

## Changelog

cl2nc follows [semantic versioning](http://semver.org/).

### 3.0.0 (2018-08-20)

- Changed `time` variable to contain time offset in seconds since
1970-01-01 00:00:00 UTC.
`time_utc` contains the original time values (UTC as ISO 8601 strings).

### 2.1.0 (2017-11-25)

- Fixed parsing on Windows (line endings).
- Added support for a specific CL31 format (timestamp line instead of checksum).

### 2.0.1 (2017-10-23)

- Fixed writing of NA integer values.
- Fixed scale factor of `backscatter_sum`.

### 2.0.0 (2017-10-19)

- **Important:** Fixed units conversion for sky condition height data and
    vertical resolution. In previous versions vertical_resolution is off
    by a factor of 0.3048 if input file units is ft. layer_height is off
    by a factor of 100 or 10 if units are ft or m, respectively.
- Added NetCDF file attributes: `software`, `version`, `created`.
- Format time with `T` as delimiter to conform to ISO 8601.
- Improved error handling.

## See also

[ccplot](https://ccplot.org),
[mpl2nc](https://github.com/peterkuma/mpl2nc),
[mrr2c](https://github.com/peterkuma/mrr2c)
