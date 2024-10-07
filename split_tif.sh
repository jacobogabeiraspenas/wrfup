#!/bin/bash

# Input TIFF file
input_tif="lambda_b_v3_real2d_correct_account_int8_3_bands.tiff"

# Get the dimensions of the input image
width=$(gdalinfo $input_tif | grep "Size is" | awk '{print $3}' | sed 's/,//')
height=$(gdalinfo $input_tif | grep "Size is" | awk '{print $4}')

# Calculate the width and height of each chunk
chunk_width=$((width / 4))
chunk_height=$((height / 4))

# Loop to create the 16 tiles
for i in {0..3}; do
    for j in {0..3}; do
        # Calculate offsets
        xoff=$((chunk_width * j))
        yoff=$((chunk_height * i))

        # Output filename
        output_tif=$(printf "%02d_%02d_URB_PARAM_100m.tif" $i $j)

        # Use gdal_translate to extract the chunk
        gdal_translate -of GTiff -srcwin $xoff $yoff $chunk_width $chunk_height $input_tif $output_tif

        echo "Created $output_tif"
    done
done

