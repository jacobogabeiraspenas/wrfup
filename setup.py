
from setuptools import setup, find_packages

setup(
    name="wrfup",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'netCDF4',
        'pandas',
        # Add more dependencies here
    ],
    # Other metadata...
)
