import setuptools, sys

setuptools.setup(
    name="eversync",
    version='0.1.0',
    license="MIT",

    author="Jianye Ye",
    author_email="yejianye@gmail.com",
    url="https://github.com/yejianye/eversync",

    description="Sync local directory with evernote notebook.",
    keywords=["evernote"],
    classifiers=[
            "Environment :: Console",
            "Development Status :: 3 - Alpha",
            "Programming Language :: Python",
            "Programming Language :: Python :: 2.7",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Natural Language :: English",
            "Operating System :: OS Independent",
            "Environment :: Other Environment",
            "Topic :: Utilities",
        ],
    entry_points={
        'console_scripts': [
            'eversync = eversync.main:main',
        ]
    },
    install_requires=['evernote', 'markdown', 'orgco'],
    packages=['eversync'],
)
