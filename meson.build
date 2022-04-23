project('caja-git', license: 'GPL-3.0-or-later', version: '0.1')

py = import('python')

python3 = py.find_installation('python3')
python3_version = python3.language_version()
if python3_version.version_compare('<3.8')
    error('Minimum Python 3.8 required')
endif

conf = configuration_data()
conf.set('PKG_DATA_DIR', get_option('prefix') / get_option('datadir') / meson.project_name())
conf.set('CAJA_EXTENSION_DIR', get_option('prefix') / get_option('datadir') / 'caja-python' / 'extensions')

subdir('data')

run_command(python3, '-m', 'compileall', meson.current_source_dir() / 'src', check: true)
install_subdir('src', install_dir: conf.get('PKG_DATA_DIR'))

configure_file(input: 'git.py.in',
               output: 'git.py',
               configuration: conf,
               install: true,
               install_dir: conf.get('CAJA_EXTENSION_DIR'))

# vim: ts=4 et
