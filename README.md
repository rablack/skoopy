# Skoopy: Skoobot Control Library and Tools

Skoopy is a Python 3 library and utilities that can be used to control the [Skoobot] mini-robot by [bweiler] using Bluetooth Low Energy on Linux.

## Installation

1. Make sure that the Python 3 version of [bluepy] is installed. See its repository for details.

2. Download and unpack the contents of this repository.

3. In the directory above the downloaded repository run:
```sh
pip3 install skoopy
```

## Commands
- `sudo skooscan` - Scan for Skoobots
- `skoocontrol` - Send a command or list of commands to a Skoobot


## See also
- [Skoobot Firmware]
- [Skoobot App for Android]

[Skoobot]: https://hackaday.io/project/75832-skoobot
[bweiler]: https://github.com/bweiler
[Skoobot Firmware]: https://github.com/bweiler/Skoobot-firmware
[bluepy]: https://github.com/IanHarvey/bluepy
[Skoobot App for Android]: https://github.com/bweiler/Android-Skoobot-Control
