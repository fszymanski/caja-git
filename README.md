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
$ meson builddir
$ sudo meson install -C builddir
#  OR
$ meson --prefix=~/.local builddir
$ meson install -C builddir
```
3. Restart Caja.
```sh
$ caja -q
```

## Credits
- The original code author [Bilal Elmoussaoui](https://github.com/bilelmoussaoui).
- The `caja-git-symbolic.svg` icon was taken from [GNOME Builder](https://wiki.gnome.org/Apps/Builder).

## Screenshot
![](assets/screenshot.png?raw=true "Caja main window")
