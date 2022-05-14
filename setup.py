"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app

Notes:
    - if you get an error about missing 'libpython3.5.dylib', make a symlink
      to 'libpython3.5m.dylib'
"""

from setuptools import setup
import platform
from otter import consts
from glob import glob

main_script = 'otter/__main__.py'
assets_dir = 'otter/assets'

if platform.system() == 'Darwin':
    PLIST_INFO = {
        'CFBundleName': consts.APP_NAME,
        'CFBundleDisplayName': consts.APP_NAME,
        'CFBundleGetInfoString': consts.DESCRIPTION,
        'CFBundleIdentifier': "name.andrs.osx.otter",
        'CFBundleVersion': str(consts.VERSION),
        'CFBundleShortVersionString': str(consts.VERSION),
        'NSHumanReadableCopyright': consts.COPYRIGHT
    }

    extra_options = dict(
        setup_requires=['py2app'],
        app=[main_script],
        data_files=[
            ('icons', glob(assets_dir + '/icons/*.svg')),
            ('icons', glob(assets_dir + '/icons/*.png')),
            ('plugins', glob('otter/plugins/*.py')),
            ('plugins/computed_vs_measured',
                glob('otter/plugins/computed_vs_measured/*.py')),
            ('plugins/csvplotter',
                glob('otter/plugins/csvplotter/*.py')),
            ('plugins/mesh_inspector',
                glob('otter/plugins/mesh_inspector/*.py')),
        ],
        options={
            'py2app': {
                'argv_emulation': False,
                'plist': PLIST_INFO,
                'iconfile': 'icon.icns',
                'packages': [
                    'vtk', 'fcntl', 'pandas', 'cmath', 'glob'
                ]
            }
        }
    )
elif platform.system() == 'win32':
    extra_options = dict(
     setup_requires=['py2exe'],
     app=[main_script],
    )
else:
    extra_options = dict(
        # Normally unix-like platforms will use "setup.py install" and install
        # the main script as such
        scripts=[main_script]
    )

setup(
    name=consts.APP_NAME,
    version=consts.VERSION,
    author='David Andrš',
    author_email='andrsd@gmail.com',
    url='https://github.com/andrsd/otter',
    license='LICENSE',
    description=consts.DESCRIPTION,
    install_requires=[
        'PyQt5-sip==12.9.0',
        'PyQt5==5.13.1',
        'PyQtChart==5.13.1',
        'cycler>=0.10.0',
        'kiwisolver>=1.1.0',
        'matplotlib>=3.1.1',
        'numpy>=1.18.1',
        'pandas>=1.3.3',
        'pycparser>=2.19',
        'pyparsing>=2.4.7',
        'python-dateutil>=2.8.1',
        'pytz>=2021.3',
        'six>=1.15.0',
        'terminaltables>=3.1.0',
        'sphinx',
        'vtk==9.0.3',
        'PyYAML>=5.4.1',
        'h5py>=3.6.0'
    ],
    packages=[
        'otter',
        'otter.assets',
        'otter.plugins',
        'otter.plugins.common',
        'otter.plugins.model_inspector',
        'otter.plugins.mesh_inspector',
        'otter.plugins.viz',
    ],
    entry_points={
        'gui_scripts': [
            'otter = otter.__main__:main',
            'model-inspector = otter.plugins.model_inspector.__main__:main',
            'mesh-inspector = otter.plugins.mesh_inspector.__main__:main',
            'viz = otter.plugins.viz.__main__:main'
        ]
    },
    include_package_data=True,
    package_data={
        'otter.assets': ['*.svg']
    },
    **extra_options
)
