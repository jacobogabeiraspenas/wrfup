for file in 02_*.tif; do
    mv "$file" "${file:3}"
done

