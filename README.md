# cl2nc

cl2nc is an open source command-line Python program for converting Vaisala
CL51, CL31 and CT25K ceilometer DAT and HIS L2 files to NetCDF.

## Example

On the command-line:

```sh
cl2nc input.dat output.nc
```

where `input.dat` is a Vaisala CL51, CL31, or CT25K DAT file and `output.nc` is
the name of a NetCDF output file.

See
[cl2nc-examples.zip](https://files.peterkuma.net/media/ttzp3npjy0/cl2nc-examples.zip)
for examples of input and output.

## Installation

It is recommended to run cl2nc on Linux.

### Linux

On Debian-derived distributions (Ubuntu, Devuan, ...), install the required
system packages with:

```sh
sudo apt install python3 python3-pip pipx
```

On Fedora, install the required system packages with:

```sh
sudo yum install python3 pipx
```

Install cl2nc:

```sh
pipx install cl2nc
mkdir -p ~/.local/share/man/man1
ln -s ~/.local/pipx/venvs/cl2nc/share/man/man1/cl2nc.1 ~/.local/share/man/man1/
```

Make sure that `$HOME/.local/bin` is included in the `PATH` environment
variable if not already. This can be done with `pipx ensurepath`.

You should now be able to run `cl2nc` and see the manual page with `man cl2nc`.

To uninstall:

```sh
pipx uninstall cl2nc
rm ~/.local/share/man/man1/cl2nc.1
```

### macOS

Open the Terminal. Install cl2nc with:

```sh
python3 -m pip install cl2nc
```

Make sure that `/Users/<user>/Library/Python/<version>/bin` is included in the
`PATH` environment variable if not already, where `<user>` is your system user
name and `<version>` is the Python version. This path should be printed by the
above command. This can be done by adding this line to the file `.zprofile` in
your home directory and restart the Terminal:

```sh
PATH="$PATH:/Users/<user>/Library/Python/<version>/bin"
```

You should now be able to run `cl2nc` and see the manual page with `man cl2nc`.

To uninstall:

```sh
python3 -m pip uninstall cl2nc
```

### Windows

Install [Python 3](https://www.python.org). In the installer, tick `Add
python.exe to PATH`.

Open Command Prompt from the Start menu. Install cl2nc with:

```sh
pip install cl2nc
```

You should now be able to run `cl2nc`.

To uninstall:

```sh
pip uninstall cl2nc
```

## Usage

cl2nc is a command-line program to be run on a terminal (Linux and macOS) or
the Command Prompt (Windows).

Synopsis:

`cl2nc` [`-chqstv`] [`--debug`] *input* *output* \
`cl2nc` `-h`|`--help`

*input* is an input `.dat` or `.his` (L2) file. *output* is an output `.nc`
file.  If directories are supplied for *input* and *output*, all `.dat`,
`.DAT`, `.his` and `.HIS` files in *input* are converted to `.nc` files in
*output*.

Options:

- `-c`: Enable DAT checksum verification (slow).
- `--debug`: Enable debugging output.
- `-h`, `--help`: Show help message and exit.
- `-q`: Run quietly (suppress output).
- `-s`: Profile sampling rate in seconds for use with files with no timestamps.
- `-t`: Initial time as *year*-*month*-*day*T*hour*:*minute*:*second* for use
  with files with no timestamps.
- `-v`: Show program's version number and exit.

On Linux and macOS, see also the manual page with:

```sh
man cl2nc
```

## Variables

Please see Vaisala CL51, CL31, or CT25K User's Guide for a complete description
of the variables.

The DAT files can alternatively contain values in feet (instead of meters), in
which case all values are converted by cl2nc to meters.

Time in DAT and HIS files is assumed to be UTC.

Missing values are encoded as NaN (floating-point variables) or -2147483648
(integer variables). The `_FillValue` attribute contains the missing value used
in the given variable.

DAT files produce the following NetCDF output:

| Variable | Description | Units | Dimensions |
| --- | --- | --- | --- |
| [background_light](#background_light) | Background light | mV | time |
| [backscatter](#backscatter) | Attenuated volume backscatter coefficient | km<sup>-1</sup>.sr<sup>-1</sup> | time, level |
| [backscatter_sum](#backscatter_sum) | Backscatter sum | sr<sup>-1</sup> | time |
| [cbh_1](#cbh_1) | Lowest cloud base height | m | time |
| [cbh_2](#cbh_2) | Second lowest cloud base height | m | time |
| [cbh_3](#cbh_3) | Highest cloud base height | m | time |
| [detection_status](#detection_status) | Detection status | | time |
| [highest_signal](#highest_signal) | Highest signal detected | | time |
| [id](#id) | Ceilometer identification string | | time |
| [laser_temperature](#laser_temperature) | Laser temperature | °C | time |
| [layer](#layer) | Layer number | | layer |
| [layer_cloud_amount](#layer_cloud_amount) | Layer cloud amount | octas | time, layer |
| [layer_height](#layer_height) | Layer height | m | time, layer |
| [level](#level) | Level number | | level |
| [measurement_mode](#measurement_mode) (CT25K) | Measurement mode | | time |
| [message_number](#message_number) | Message number | | time |
| [message_subclass](#message_subclass) | Message subclass | | time |
| [pulse_energy](#pulse_energy) | Pulse energy | % | time |
| [pulse_length](#pulse_length) | Pulse length | | time |
| [pulse_count](#pulse_count) | Pulse count | | time |
| [receiver_bandwidth](#receiver_bandwidth) | Receiver bandwidth | | time |
| [receiver_gain](#receiver_gain) | Receiver gain | | time |
| [receiver_sensitivity](#receiver_sensitivity) (CT25K) | Receiver sensitivity | % | time |
| [sampling](#sampling) | Sampling | Hz | time |
| [self_check](#self_check) | Self check | | time |
| [sky_detection_status](#sky_detection_status) | Sky detection status | | time |
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
| [window_contamination](#window_contamination) | Window contamination | mV | time |

HIS L2 files produce the following NetCDF output:

| Variable | Description | Units | Dimensions |
| --- | --- | --- | --- |
| [backscatter](#backscatter) | Attenuated volume backscatter coefficient | km<sup>-1</sup>.sr<sup>-1</sup> | time, level |
| [ceilometer](#ceilometer) | Ceilometer name | | time |
| [level](#level) | Level number | | level |
| [period](#period) | Period | | time |
| [time](#time) | Time | seconds since 1970-01-01 00:00:00 UTC | time |
| [time_utc](#time_utc) | Time (UTC) | ISO 8601 | time |

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

### ceilometer

Ceilometer name (HIS L2 variable `CEILOMETER`).

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
- -1 – data missing, sky condition option not active or ceilometer in standby
  mode
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

### measurement_mode (CT25K)

Measurement mode

- N – normal
- C – close range

### message_number

Message number

- 1 – message without sky condition data
- 2 – message with sky condition data

### message_subclass

Message subclass

- 6 – 10 m ⨉ 1540 samples, range 15400 m (msg1_10x1540)
- 8 – without a backscatter profile (msg1_base)

### period

Period (HIS L2 variable `PERIOD`).

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

### receiver_sensitivity

Receiver sensitivity (%)

### sampling

Sampling (Hz)

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

Flags (CT25K):

- 0x80 – laser temperature shut-off
- 0x40 – laser failure
- 0x20 – receiver failure
- 0x10 – voltage failure

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
- 0x0080 – units are meters if on, else feet (note that units are always
  converted to m by cl2nc)
- 0x0040 – manual blower control
- 0x0020 – polling mode is on

Flags (CT25K):

- 0x800 – blower is on
- 0x400 – blower heater is on
- 0x200 – internal heater is on
- 0x100 – units are meters if on, else feet (note that units are always
  converted to m by cl2nc)
- 0x080 – polling mode is on
- 0x040 – working from battery
- 0x020 – single sequence mode is on
- 0x010 – manual settings are effective
- 0x008 – tilt angle > 45°
- 0x004 – high background radiance
- 0x002 – manual blower control

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
- 0x0002 – tilt angle > 45° warning

Flags (CT25K):

- 0x800 – window contamination
- 0x400 – battery low
- 0x200 – laser power low
- 0x100 – laser temperature high or low
- 0x080 – internal temperature high or low
- 0x040 – voltage high or low
- 0x020 – relative humidity > 85% (option)
- 0x010 – receiver optical cross-talk compensation poor
- 0x008 – blower suspect

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

This software is open source and can be used, shared, and modified freely under
the terms of the MIT License (see [LICENSE.md](LICENSE.md)).

## Support

If you encounter any issues with cl2nc you can contact me at Peter Kuma
<<peter@peterkuma.net>> or submit a [GitHub
Issue](https://github.com/peterkuma/cl2nc/issues).

## Known issues

There are many different undocumented variants of the CL31/CL51 format in use.
cl2nc strives to support most of them, but if you encounter errors with your
data files, it might be because it is yet another variant. In such a case,
submit a [GitHub Issue](https://github.com/peterkuma/cl2nc/issues).

## FAQ

### cl2nc fails with an exception.

Please make sure that the Python package netCDF4 is installed. If it still does
not work for you, contact me: Peter Kuma <<peter@peterkuma.net>>.  There are
small variations in the .DAT file format with instruments.  cl2nc may need to
be modified to be able to read a particular type of format.

### Where is the height information?

Height can be determined from [vertical_resolution](#vertical_resolution).  The
instrument samples vertical bins at regular intervals.

### MATLAB cannot read the time_utc variable.

MATLAB NetCDF implementation currently does not support reading NC_STRING
variables. You can use the `time` variable instead or use the MATLAB HDF
functions to read the file (you may need to change the file extension to
`.h5`).

## Changelog

cl2nc follows [semantic versioning](http://semver.org/).

### 3.6.0 (2024-09-10)

- Added support for the CT25K ceilometer.
- Improved output metadata.

### 3.5.0 (2024-04-18)

- Added support for the HIS L2 format.

### 3.4.0 (2023-03-10)

- Added support for a CL51 format as in R/V Polarstern data.

### 3.3.2 (2023-02-26)

- Issue a warning when no output was created because an input file is empty.

### 3.3.1 (2021-03-24)

- Fixed an issue of the last record in DAT files being skipped.

### 3.3.0 (2020-08-27)

- Fixed handling of certain types of time encoding.
- Issue a warning instead of an error when a line cannot be parsed.

### 3.2.2 (2020-07-17)

- Fixed installation on Windows.

### 3.2.1 (2020-02-08)

- Added manual page.

### 3.2.0 (2020-02-08)

- Support for an alternative DAT format with UNIX timestamps.
- Improved error logging.
- New option: `--debug`.

### 3.1.0 (2019-04-27)

- Support for Python 3.
- Accept directory input and output arguments.

### 3.0.0 (2018-08-20)

- Changed `time` variable to contain time offset in seconds since
1970-01-01 00:00:00 UTC.
`time_utc` contains the original time values (UTC as ISO 8601 strings).

### 2.1.0 (2017-11-25)

- Fixed parsing on Windows (line endings).
- Added support for a specific CL31 format (timestamp line instead of
  checksum).

### 2.0.1 (2017-10-23)

- Fixed writing of NA integer values.
- Fixed scale factor of `backscatter_sum`.

### 2.0.0 (2017-10-19)

- **Important:** Fixed units conversion for sky condition height data and
  vertical resolution. In previous versions, vertical_resolution is off by a
  factor of 0.3048 if input file units are ft. layer_height is off by a factor
  of 100 or 10 if units are ft or m, respectively.
- Added NetCDF file attributes: `software`, `version`, `created`.
- Format time with `T` as a delimiter to conform to ISO 8601.
- Improved error handling.

## See also

[ALCF](https://alcf-lidar.github.io),
[ccplot](https://ccplot.org),
[ccbrowse](https://github.com/peterkuma/ccbrowse),
[mpl2nc](https://github.com/peterkuma/mpl2nc),
[mrr2c](https://github.com/peterkuma/mrr2c)
