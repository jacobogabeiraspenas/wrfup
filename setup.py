from setuptools import setup, find_packages

setup(
    name='wrfup',  # The name of your package
    version='1.0.0',  # Package version
    description='A Python package for ingesting urban data into WRF geo_em files.',
    long_description=open('README.md').read(),  # Include README as long description
    long_description_content_type='text/markdown',
    url='https://github.com/jacobogabeiraspenas/UrbanSurfAce/',  # Your package's GitHub URL
    author='Jacobo Gabeiras Penas',
    author_email='jacobogabeiras@gmail.com',  # Your contact email
    license='MIT',  # License type
    packages=find_packages(),  # Include all packages
    install_requires=[
        'numpy',
        'tqdm',
        'requests',
        'netCDF4',
        'pandas',
        'shapely',
        'fiona',
        'ipyleaflet',
        'ipywidgets',
        'xarray',
        'scipy',
    ],
    entry_points={
        'console_scripts': [
            'wrfup=wrfup.main:main',  # Command-line tool setup
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

