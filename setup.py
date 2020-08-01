from distutils.core import setup

setup(
    name='InteractionFreePy',
    packages=['InteractionFreePy'],
    version='1.0.0',
    license='gpl-3.0',
    description='A intuitive and cross-languige RCP lib for Python.',
    author='Hwaipy',
    author_email='hwaipy@gmail.com',
    url='https://github.com/hwaipy/InteractionFreePy',
    download_url='https://github.com/user/reponame/archive/v_01.tar.gz',  # I explain this later on
    keywords=['msgpack', 'zeromq', 'zmq', '0mq', 'rcp', 'cross-languige'],
    install_requires=[  # I get to this in a second
        # 'validators',
        # 'beautifulsoup4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: RCP',
        'License :: OSI Approved :: GNU Lesser General Public License v3.0',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
