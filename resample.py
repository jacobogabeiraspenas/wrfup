import rasterio
from rasterio.enums import Resampling

input_file = 'urban_fraction_100m.tif'
output_file = 'urban_fraction_100m_modified.tif'

with rasterio.open(input_file) as src:
    data = src.read(out_dtype='float32', resampling=Resampling.bilinear)
    # Scale the data
    scaled_data = (data * 100).astype('int16')
    
    profile = src.profile
    # Update the profile to reflect the changes: data type and compression
    profile.update(dtype=rasterio.int16, compress='lzw')
    
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(scaled_data)

