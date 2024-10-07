from setuptools import setup, find_packages

setup(
    name="wrfup",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'wrfup': ['config.yaml'],  # Include the YAML file in the package
    },
    entry_points={
        'console_scripts': [
            'wrfup = wrfup.main:main',
        ],
    },
    install_requires=[
        'xarray',
        'rasterio',
        'numpy',
        # Add other dependencies here
    ],
)

