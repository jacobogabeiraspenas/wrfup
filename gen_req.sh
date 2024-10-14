# Here is a bash script that lists the versions of the required packages in your current environment:

echo "Installed versions of required packages:"
echo "numpy: $(python -c 'import numpy; print(numpy.__version__)')"
echo "tqdm: $(python -c 'import tqdm; print(tqdm.__version__)')"
echo "requests: $(python -c 'import requests; print(requests.__version__)')"
echo "netCDF4: $(python -c 'import netCDF4; print(netCDF4.__version__)')"
echo "pandas: $(python -c 'import pandas; print(pandas.__version__)')"
echo "shapely: $(python -c 'import shapely; print(shapely.__version__)')"
echo "fiona: $(python -c 'import fiona; print(fiona.__version__)')"
echo "rasterio: $(python -c 'import rasterio; print(rasterio.__version__)')"
echo "xarray: $(python -c 'import xarray; print(xarray.__version__)')"
echo "scipy: $(python -c 'import scipy; print(scipy.__version__)')"



