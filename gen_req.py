import pkg_resources

# List of relevant packages to check the installed version
packages = [
    'numpy', 'tqdm', 'requests', 'netCDF4', 'pandas', 'shapely', 'fiona', 
    'rasterio', 'xarray', 'scipy', 'sphinx_rtd_theme'
]

# Retrieve and print installed versions of these packages
installed_packages = {pkg.key: pkg.version for pkg in pkg_resources.working_set if pkg.key in packages}
installed_packages

