# edit_oem_rom_project

[![Donate with PayPal](https://raw.githubusercontent.com/stefan-niedermann/paypal-donate-button/master/paypal-donate-button.png)](http://paypal.me/abdd1997)

edit_oem_rom_project is a utility for Unpack and Repack OEM Firmware.

## Supported Firmware

- Xiaomi (brotli)
- OnePlus (payload.bin)
- Motorola (super.img_sparsechunk.*)

## Requirements

- Linux
- Wsl version 1 recommended (wsl2 slow)
- Termux with ubuntu arm64
- python3 greater than 3.6

```bash
pip install -r requirements.txt
```

### Usage

```
usage: main.py [-h] [-n NAME] [-i INPUT] [-u PRJ_NAME] [-l] [-w] [-R] [-S] [-B] [--clean] [--version]

options:
  -h, --help          show this help message and exit
  -n NAME             Specify project name and init folder project
  -i INPUT            Input zip
  -u PRJ_NAME         Update project name in config.ini
  -l                  List of projects
  -w, --write-config  Write config.ini
  -R                  Build ext4 image (linux only)
  -S                  Build Sparse image (linux only) with [-R]
  -B                  Build .sdat.br image (linux only) with [-RS]
  --clean             Clean up projects dir
  --version           Display version
```

## Download

```
git clone https://github.com/abdalrohman/edit_oem_rom_project.git
```

## Unpack firmware

Example:

```
cd edit_oem_rom_project
./main.py -w   # Write config.ini before unpack firmware
./main.py -n <project name> -i <path to firmware zip>
```

## Repack firmware

Example: Make ext4:

```
cd edit_oem_rom_project
./main.py -n <project name> -R
```

Example: Make Sparse:

```
cd edit_oem_rom_project
./main.py -n <project name> -S
```

Example: Compress with brotli:

```
cd edit_oem_rom_project
./main.py -n <project name> -B
```

Example: All option in one command (must be ordered):

```
cd edit_oem_rom_project
./main.py -n <project name> -RSB
```

Example: Clean Projects:

```
cd edit_oem_rom_project
./main.py --clean
```

Example: Install with fastboot:

```
cd edit_oem_rom_project
./main.py -u <project name>
./install.py
```

## Contributing

Feel free to add or improve this project :) Just create a pull request and explain the changes you propose.

### Todo

- [x] Support extract raw filesystem
- [x] Support extract erofs filesystem
- [x] Support extract brotli compressing
- [x] Support extract super.img <.gz, .zst, .br>
- [x] Support extract sparse
- [x] Support install with fastboot
- [x] Support working with multi project
- [x] Support Termux
- [x] Repack firmware as brotli
- [ ] Repack firmware as super image
- [ ] Repack firmware as erofs
- [ ] Add support to extra script
- [ ] Deodexed firmware
- [ ] Patch apk
- [ ] Debloat firmware
- [ ] Make project name like zip if [-n] not specified
- [ ] Update context and config if new files add to firmware
- [ ] Unpack/Repack boot.img
- [ ] Unpack/Repack dtbo.img
- [ ] Patch vbmeta
- [ ] Generate firmware zip when finish
- [ ] Support windows without wsl

## Tools used from other project

### [cubinator/ext4](https://github.com/cubinator/ext4)

GPL 3

### [ssut/payload-dumper-go](https://github.com/ssut/payload-dumper-go)

Apache 2.0

### [sekaiacg/erofs-extract](https://github.com/sekaiacg/erofs-extract)

## License

edit_oem_rom_project is licensed under the [GPL 3 licensed](LICENSE) as described in the LICENSE file.
