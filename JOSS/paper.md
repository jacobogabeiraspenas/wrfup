# wrfup: The WRF Urban Parameters Toolkit
### A Python Tool for Ingesting Urban Morphology Data into WRF Simulations


*Author:*  Jacobo Gabeiras  
Univ. Grenoble Alpes, CNRS, Grenoble INP, LEGI, Grenoble, 38000, France  
*Email:* Jacobo.Gabeiras-Penas@univ-grenoble-alpes.fr  


### Summary

*wrfup* is a Python-based tool that significantly enhances urban climate modeling in the Weather Research and Forecasting (WRF) model by automating the sourcing and ingestion of high-resolution urban morphology data. This package calculates crucial urban canopy parameters—*URB_PARAM* and *FRC_URB2D*—enabling precise simulations for advanced urban canopy parameterizations like SLUCM, BEP, and BEP+BEM. This tool streamlines the traditionally complex process of integrating detailed city-specific data into WRF simulations, providing researchers with an accessible, fast, and scientifically robust workflow through a simple terminal command. This increased efficiency makes *wrfup* particularly valuable for urban climate studies, where accuracy in the granularity of data are crucial for predicting phenomena like the urban heat island effect or simulating effective adaptation strategies.


### Statement of Need

Accurately simulating urban climate and weather phenomena, such as the urban heat island (UHI) effect, altered wind patterns, and precipitation dynamics, is critical for improving research on local climate and effective adaptation strategies. The *Weather Research and Forecasting (WRF)* model offers advanced urban parameterizations—*SLUCM (Single-Layer Urban Canopy Model)*, *BEP (Building Effect Parameterization)*, and *BEP+BEM (Building Energy Model)* [@bepplusbem]—which enable precise simulations of these urban effects. However, these parameterizations depend heavily on high-quality data describing the urban morphology, including building heights, building fraction and others.

High-resolution datasets from *LiDAR* measurements provide accurate urban morphology data but are often difficult to process, complex to integrate into models, and not universally available, especially in developing cities. The *WUDAPT (World Urban Database and Access Portal Tools)* [@EUWUDAPT] project addresses this gap by offering the *Local Climate Zone (LCZ)* framework, which clasifies urban areas into distinct zones based on physical characteristics. The *LCZ Generator* [@lczgenerator] and *W2W (WUDAPT to WRF)* [@w2w] further enhance and facilitate the integration process of LCZ data into the WRF model. However, this approach relies on generalized table values rather than specific, detailed urban structure data, which limits the accuracy of the simulations.

The *wrfup* package offers an easy and quick way to integrate real-world urban data into WRF’s *geo_em* files. It significantly simplifies the process compared to the time-consuming task of manually processing local urban data, delivering results much faster while maintaining accuracy. This makes it a more efficient alternative to traditional LIDAR approaches, and more accurate than generalized data table values. *wrfup* supports advanced urban parameterizations (*SLUCM*, *BEP*, and *BEP+BEM*), allowing for detailed simulations that accurately reflect accurate city-specific characteristics. It also complements *W2W*, while bridging the gap for simulating urban environments more precisely and effectively.


### Software Description


The tool works by calculating and ingesting the fields *URB_PARAM* and *FRC_URB2D*, which contain critical information for representing urban surfaces in the WRF model. *URB_PARAM* is a field in the WRF urban models, containing the needed information of buildings, such as the building heights, or planar building fraction, while *FRC_URB2D* represents the fraction of urban land in each grid cell.

The *wrfup* package is structured around modules that handle downloading data, calculating necessary fields, and ingesting them into WRF’s *geo_em* files.

- *Main Module*: The entry point of the package, which allows users to run commands from the terminal.
- *Download Module*: Automates the process of downloading urban morphology data for a given area of interest (AOI). The data sources include *World Settlement Footprint 3D (WSF3D)* [@wsf3d], *Global Urban Fraction* [@urban_fraction] and *UrbanSurfAce Project*.
- *Calculation Module*: Responsible for calculating urban parameters in the field URB_PARAM following the system of National Urban Data and Access Portal Tool (NUDAPT). These fields are:
    - In field FRC_URB2D.
        - *Urban Fraction*.
    - In field URB_PARAM:
        - *Plan Area Fraction* stored in slice [90,:,:]
        - *Mean Building Height* stored in slice [91,:,:]
        - *Standard deviation of Building Height* stored in slice [92,:,:]
        - *Weighted Building Height* stored in slice [93,:,:]
        - *Frontal Area Fraction* stored in slice [94,:,:]
        - *Frontal Area Index* stored in slices [95-98,:,:] for different wind directions
        - *Building Height Distribution* stored in slices [117:132,:,:]
    
- *Utility Module*: Handles tasks such as cleaning temporary files, verifying geo_em file integrity, and managing the output of modified *geo_em* files.

### Initial Data Requirements

To use *wrfup* effectively, the primary requirement is a *geo_em.d0X.nc* file for the specific inner domain of the WRF model. This file is generated by the WRF Preprocessing System (WPS) using *geogrid.exe*, following the standard procedure without needing any additional modifications to the *namelist.wps* file.

In cases where the *URB_PARAM* or *FRC_URB2D* fields are missing from the *geo_em* file, wrfup automatically creates these fields. It follows the required attributes and structure within the WRF framework to ensure compatibility with urban canopy models. 

### Workflow Overview

The entire process for preparing and modifying urban canopy parameters for the Weather Research and Forecasting (WRF) model using *wrfup* is handled through a single terminal command. This command allows the user to update the *geo_em.d0X.nc* file by calculating and ingesting the necessary urban parameters, depending on the specified target (either *URB_PARAM* or *FRC_URB2D*).

The execution involves running the following command in the CLI (Command Line Interface):

```bash
wrfup geo_em.d0X.nc URB_PARAM --work_dir YOUR_DIRECTORY
```

or

```bash
wrfup geo_em.d0X.nc FRC_URB2D --work_dir YOUR_DIRECTORY
```

The tool updates the *geo_em* file, calculating the urban canopy parameters and generating a new modified output file (e.g., *geo_em_URB_PARAM.nc* or *geo_em_FRC_URB2D.nc*), ready for subsequent steps in the WRF modeling workflow. 

This streamlined approach eliminates the need for manual data handling and complex processing, allowing researchers to quickly integrate real-world building data into WRF simulations.


### Integration in WRF’s Preprocessing

The *wrfup* tool is designed to work seamlessly with the Weather Research and Forecasting (WRF) Preprocessing System (WPS). The workflow integrates *wrfup* with WRF’s Preprocessing System like shown in figure 1. 

1. First, *geogrid* generates the initial *geo_em.d0X.nc* file that contains the necessary geographical data for WRF.
2. Using *wrfup*, the urban canopy parameters are calculated and added to the file. If the *URB_PARAM* or *FRC_URB2D* fields are not present in the file, *wrfup* creates them following the required attributes of the WRF framework. The output file, such as *geo_em_URB_PARAM.d0X.nc*, contains the detailed urban morphology required for accurate simulations.
3. This file can be renamed as *geo_em.d0X.nc* or passed directly to *metgrid* for further processing.
4. The *metgrid* tool integrates the updated *geo_em* file with meteorological data, preparing the input files for the WRF simulation.
5. Finally, these preprocessed files are used by the *real* and *wrf* executables to run the actual weather or climate simulation, incorporating precise urban morphology data into the model.


![Workflow Diagram Scheme](https://raw.githubusercontent.com/jacobogabeiraspenas/wrfup/main/docs/source/_static//workflow_wrfup.png)

Figure 1. Integration of wrfup package within the WRF Preprocessing System workflow. The *wrfup* python package generates a new *geo_em* file. This file is represented in the figure as *geo_em_new.d0X.nc* which will typically take the name of *geo_em_URB_PARAM.d0X.nc* or *geo_em_FRC_URB2D.d0X.nc*. This file needs to be then renamed as the original file to continue the WPS workflow. 

### Important Notes

When using *wrfup* to modify *geo_em* files and integrate urban morphological data into WRF simulations, these are some considerations to keep in mind:

- *Compatibility with WRF Versions*: Ensure that your WRF version supports the *URB_PARAM* and *FRC_URB2D* fields. *wrfup* requires *WPS version 3.8 or higher* for full compatibility with these urban fields and urban parameterization schemes like *SLUCM*, *BEP*, and *BEP+BEM*. Earlier versions may not properly integrate the urban parameters needed for accurate simulations.

- *Handling Large Datasets*: For large urban areas, it's important to ensure your system has adequate memory and processing power. The tool will always ask for permission to proceed before downloading any dataset.

- *Creating and Naming Output Files*: After modifying the *geo_em* files, it is important to adhere to WRF’s naming conventions. This meand renaming the *geo_em_URB_PARAM.d0X.nc* or *geo_em_FRC_URB2D.d0X.nc* back to *geo_em.d0X.nc* before running *metgrid.exe* in WPS. This will esure the model's processing system fo fetch the correct file.

- *Inspecting Updated URB_PARAM Fields*: It is recommended to validate the correctness of the updated *URB_PARAM* fields by using visualization tools like *xarray* or *ncview*.



### References

- *Marconcini, M., Esch, T., Metz, A., et al.* (2021). *World Settlement Footprint 3D - A first three-dimensional survey of the global building stock*. ResearchGate. Available at: [https://www.researchgate.net/publication/357678737_World_Settlement_Footprint_3D_-_A_first_three-dimensional_survey_of_the_global_building_stock](https://www.researchgate.net/publication/357678737_World_Settlement_Footprint_3D_-_A_first_three-dimensional_survey_of_the_global_building_stock)

- *Pablo d'Entremont et al.* (2022). *Urban Fraction Data*. Zenodo. Available at: [https://zenodo.org/records/6994975](https://zenodo.org/records/6994975)

- *Demuzere, M., Argüeso, D., Zonato, A., Kittner, J.* (2022). *W2W: A Python package that injects WUDAPT's Local Climate Zone information in WRF*. Journal of Open Source Software, 7(76), 4432. Available at: [https://doi.org/10.21105/joss.04432](https://doi.org/10.21105/joss.04432)

- *Salamanca, F., Krpo, A., Martilli, A., Clappier, A.* (2010). *A new building energy model coupled with an urban canopy parameterization for urban climate simulations—part I. formulation, verification, and sensitivity analysis of the model*. Theoretical and Applied Climatology, 99(3), 331-344. Available at: [https://doi.org/10.1007/s00704-009-0142-9](https://doi.org/10.1007/s00704-009-0142-9)

- *Demuzere, M., Bechtel, B., Middel, A., Mills, G.* (2019). *Mapping Europe into local climate zones*. PLOS ONE, 14(4), 1-27. Available at: [https://doi.org/10.1371/journal.pone.0214474](https://doi.org/10.1371/journal.pone.0214474)

- *Demuzere, M., Kittner, J., Bechtel, B.* (2021). *LCZ Generator: A Web Application to Create Local Climate Zone Maps*. Frontiers in Environmental Science, 9. Available at: [https://doi.org/10.3389/fenvs.2021.637455](https://doi.org/10.3389/fenvs.2021.637455)
