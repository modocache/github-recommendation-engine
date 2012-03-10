from setuptools import setup

setup(
    name='github-suggestion-engine',
    version='0.0.1a1',
    url='https://github.com/modocache/github-recommendation-engine',
    author='modocache',
    author_email='modocache@gmail.com',
    description='A Github repository recommendation engine.',
    long_description=\
    """
    Outputs a list of Github repositories you might be interested
    in following. Note that this makes a large amount of API
    requests, which are throttled to 60 per minute.

    For more information, check out the
    `repository on Github <https://github.com/modocache/github-recommendation-engine>`_.
    """,
    keywords='githubt repository follow',
    install_requires=['github2'],
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Software Development :: Version Control',
    ],
    entry_points = {
        'console_scripts': [
            'github-suggestion-engine = engine:main',
        ]
    }
)
