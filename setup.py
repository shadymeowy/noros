from setuptools import setup

setup(
    name='noros',
    version='0.0.1',
    description='A simple ROS-like message passing library based on ZeroMQ',
    author='Tolga Demirdal',
    url='https://github.com/shadymeowy/noros',
    setup_requires=[],
    install_requires=['pyzmq'],
    packages=['noros', 'noros.helpers'],
    entry_points={
        'console_scripts': [
            'noros = noros.cli:main',
            'noros-mavlink = noros.helpers.mavlink:mavlink_bridge',
        ],
    },
)
