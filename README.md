# caja-git

## General Information
Caja extension that shows information about the current git directory. This project is based on [caja-git](https://github.com/darkshram/caja-git) by [Joel Barrios](https://github.com/darkshram).

## Dependencies
- `git`
- `python3-caja`

## Installation
1. Clone the extension repository.
```sh
$ git clone https://github.com/fszymanski/caja-git.git
$ cd caja-git
```
2. Build and install the extension.
```sh
# Note: Omit the `--prefix` if you want to install globally
$ meson --prefix=~/.local builddir
$ ninja -C builddir install
```
3. Restart Caja.
```sh
$ caja -q
```

## Uninstallation
1. Uninstall the extension.
```sh
$ cd caja-git
$ ninja -C builddir uninstall
```
2. Restart Caja.
```sh
$ caja -q
```

## Credits
- The original code author [Bilal Elmoussaoui](https://github.com/bilelmoussaoui).
- The `caja-git-symbolic.svg` icon was taken from [GNOME Builder](https://wiki.gnome.org/Apps/Builder).

## Screenshot
![](assets/screenshot.png?raw=true "Caja main window")
