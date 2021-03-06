# Skoopy: Skoobot Control Library and Tools

Skoopy is a Python 3 library and utilities that can be used to control the [Skoobot] mini-robot by [bweiler] using Bluetooth Low Energy on Linux.

## Installation

1. Make sure that the Python 3 version of [bluepy] is installed. See its repository for details.

2. Download and unpack the contents of this repository.

3. In the directory above the downloaded repository run:
```sh
sudo pip3 install skoopy
```

## Commands
- `sudo skooscan` - Scan for Skoobots
- `skoocontrol` - Send a command or list of commands to a Skoobot

For further information, run each command with the `--help` flag, e.g.
```sh
skoocontrol --help
```

## Troubleshooting
### File not Found in skooscan
If skooscan gives a File not Found error, this usually means that it cannot
work out the logname of the logged in user. Certain Linux variants (such as
Raspbian) do not update the login database when they auto-login users.

For commands run with `sudo` the current user and the login user are different.
The skooscan command uses this information to work out your home directory.

The workaround is to execute the `login` command before running `sudo skooscan`.

## See also
- [Skoobot Firmware]
- [Skoobot App for Android]

[Skoobot]: https://hackaday.io/project/75832-skoobot
[bweiler]: https://github.com/bweiler
[Skoobot Firmware]: https://github.com/bweiler/Skoobot-firmware
[bluepy]: https://github.com/IanHarvey/bluepy
[Skoobot App for Android]: https://github.com/bweiler/Android-Skoobot-Control
