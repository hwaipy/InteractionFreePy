from distutils.core import setup

setup(
    name='interactionfreepy',
    packages=['interactionfreepy'],
    version='1.0.7',
    license='gpl-3.0',
    description='A intuitive and cross-languige RCP lib for Python.',
    author='Hwaipy',
    author_email='hwaipy@gmail.com',
    url='https://github.com/hwaipy/InteractionFreePy',
    download_url='https://github.com/hwaipy/InteractionFreePy/archive/v1.0.7.tar.gz',
    keywords=['msgpack', 'zeromq', 'zmq', '0mq', 'rcp', 'cross-languige'],
    install_requires=[
        'msgpack',
        'tornado',
        'pyzmq',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
