import os
from setuptools import setup

# Utility function to read the README file.  
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "xcal3d",
    version = "0.1.0",
    author = "Emanuele Ruffaldi",
    author_email = "emanuele.ruffaldi@gmail.com",
    description = ("A package to load and manipulate Virtual Human CAL3D files directly in  Python"),
    license = "BSD",
    keywords = "cal3d avatar",
    url = "https://github.com/eruffaldi/pyxcal3d",
    packages=['xcal3d'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
