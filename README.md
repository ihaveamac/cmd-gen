# cmd-gen

Experimental script to generate CMD files for Nintendo 3DS SD titles.

**Please do not make tutorials on this program yet. The tools are very early in development and not ready for general use.**

The CMD format is explained on [3DBrew](https://www.3dbrew.org/wiki/Titles#Data_Structure).

## Setup
movable.sed is required and can be provided with `-m` or `--movable`.

boot9 is needed:
* `-b` or `--boot9` argument (if set)
* `BOOT9_PATH` environment variable (if set)
* `%APPDATA%\3ds\boot9.bin` (Windows-specific)
* `~/Library/Application Support/3ds/boot9.bin` (macOS-specific)
* `~/.3ds/boot9.bin`
* `~/3ds/boot9.bin`

## Usage

Use `-h` to view arguments.

Example:
```
cmd-gen.py -b boot9.bin -m movable.sed -t 00000000.tmd
```

## License/Credits
`pyctr/` is from [ninfs `80a4fb3`](https://github.com/ihaveamac/ninfs/tree/80a4fb387a56854973ea5498d3916b46f19f08a5/ninfs/pyctr) with some files removed.

Thanks to @BpyH64 for [researching how to generate the cmacs](https://github.com/d0k3/GodMode9/issues/340#issuecomment-487916606).
