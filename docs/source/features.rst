Features
========

**wrfup** offers the following functionalities to improve urban weather modeling in WRF:

1. **Download Urban Data**:
   Easily download **urban fraction** and **urban parameter** tiles for your area of interest.
   
2. **Calculate Fields**:
   The package computes essential fields for WRF, including:
   
   - **FRC_URB2D**: Urban Fraction of the grid cells.
   - **URB_PARAM**: A range of urban canopy parameters such as **Plan Area Fraction**, **Mean Building Height**, and **Frontal Area Index**.

3. **Ingest Data**:
   Automatically insert calculated urban morphology fields into WRF's **geo_em** files.

4. **Command-Line Interface**:
   Simplified command-line interface that allows you to download, calculate, and ingest urban data seamlessly.

---

Data Sources:
---------------------

- **World Settlement Footprint 3D**: Provides detailed global building stock data.
- **Urban Fraction Data**: For more accurate urban fraction values at various grid levels.


