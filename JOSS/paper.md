---
title: "WRFUP: A Python Package to Enhance Urban Simulations"
tags:
  - Python
  - WRF
  - Urban Canopy Parameters
  - Urban Climate Modeling
  - Geospatial Data
  - Urban Morphology
authors:
  - name: Jacobo Gabeiras^[corresponding author]
    affiliation: 1
    orcid: 0000-0000-0000-0000
  - name: Chantal Staquet
    affiliation: 1
  - name: Charles Chemel
    affiliation: 2
  - name: Alberto Martilli
    affiliation: 3
affiliations:
  - name: Université Grenoble Alpes, CNRS, Grenoble INP, LEGI, France
    index: 1
  - name: National Centre for Atmospheric Science, NCAS, Leeds, UK
    index: 2
  - name: Centro de Investigaciones Energéticas, Medioambientales y Tecnológicas, CIEMAT, Spain
    index: 3
date: 2025-XX-XX
bibliography: paper.bib
---

# Summary

WRFUP is a Python package designed to enhance urban climate modeling in the Weather Research and Forecasting (WRF) model by automating the sourcing and ingestion of high-resolution urban morphology data. This package calculates crucial urban canopy parameters—URB_PARAM and FRC_URB2D—enabling precise simulations for advanced urban canopy parameterizations like SLUCM, BEP, and BEP+BEM. This tool streamlines the traditionally complex process of integrating detailed city-specific data into WRF simulations, providing researchers with an accessible, fast, and scientifically robust workflow through a simple terminal command. This increased efficiency makes WRFUP particularly valuable for urban climate studies, where accuracy in the granularity of data are crucial for predicting phenomena like the urban heat island effect or simulating effective adaptation strategies.

# Statement of need

Accurately simulating urban climate and weather phenomena, such as the urban heat island (UHI) effect, altered wind patterns, and precipitation dynamics, is critical for improving research on local climate and effective adaptation strategies. The Weather Research and Forecasting (WRF) model offers advanced urban parameterizations—SLUCM (Single-Layer Urban Canopy Model), BEP (Building Effect Parameterization), and BEP+BEM (Building Energy Model) [@Salamanca2010]—which enable precise simulations of these urban effects. However, these parameterizations depend heavily on high-quality data describing the urban morphology, including building heights, building fraction and others.

High-resolution datasets from LiDAR measurements provide accurate urban morphology data but are often difficult to process, complex to integrate into models, and not universally available, especially in developing cities. The WUDAPT project [@Ching2018] addresses this gap by offering the Local Climate Zone (LCZ) framework, which clasifies urban areas into distinct zones based on physical characteristics. The LCZ Generator [@Demuzere2021] and W2W [@Demuzere2022] further enhance and facilitate the integration process of LCZ data into the WRF model. However, this approach relies on generalized table values rather than specific, detailed urban structure data, which limits the accuracy of the simulations.

The WRFUP package offers an easy and quick way to integrate real-world urban data into WRF’s geo_em files. It significantly simplifies the process compared to the time-consuming task of manually processing local urban data, delivering results much faster while maintaining accuracy. This makes it a more efficient alternative to traditional LiDAR approaches, and more accurate than generalized data table values. WRFUP supports advanced urban parameterizations (SLUCM, BEP, and BEP+BEM), allowing for detailed simulations that accurately reflect accurate city-specific characteristics. It also complements W2W, while bridging the gap for simulating urban environments more precisely and effectively.

# Software Description

The WRFUP package, available on GitHub [@Gabeiras2024] or via PyPI, works by calculating and ingesting the fields URB_PARAM and FRC_URB2D, which contain critical information for representing urban surfaces in the WRF model. URB_PARAM is a field in the WRF urban models, containing the needed information of buildings, such as the building heights, or planar building fraction, while FRC_URB2D represents the fraction of urban land in each grid cell.

The WRFUP package is structured around modules that handle downloading data, calculating necessary fields, and ingesting them into WRF’s geo_em files.

• Main Module: The entry point of the package, which allows users to run commands from the terminal.

• Download Module: Automates the process of downloading urban morphology data for a given area of interest (AOI). The data sources include World Settlement Footprint 3D [@Esch2022], Global Urban Fraction [@Patel2022] and UrbanSurfAce Project [@Gabeiras2025].

• Utility Module: Handles tasks such as cleaning temporary files, verifying geo_em file integrity, and managing the output of modified geo_em files.

• Calculation Module: Responsible for calculating urban parameters in the field URB_PARAM following the system of National Urban Data and Access Portal Tool [@Glotfelty2013]. These fields and their corresponding position are shown in Table 1.

**Table 1: Urban parameters stored in WRF fields with Fortran and Python indexing**

| WRF Field     | Variable                                 | Units    | Python Indexing     |
|---------------|-------------------------------------------|----------|----------------------|
| FRC_URB2D     | Urban Fraction                            | Fraction | —                    |
| URB_PARAM     | Plan Area Fraction                        | Fraction | [:,:,90]             |
| URB_PARAM     | Mean Building Height                      | Meters   | [:,:,91]             |
| URB_PARAM     | Std. Dev. of Building Height              | Meters   | [:,:,92]             |
| URB_PARAM     | Weighted Building Height                  | Meters   | [:,:,93]             |
| URB_PARAM     | Frontal Area Fraction                     | Fraction | [:,:,94]             |
| URB_PARAM     | Frontal Area Index (N, S, E, W)           | Fraction | [:,:,95:99]          |
| URB_PARAM     | Building Height Distribution              | Fraction | [:,:,117:133]        |

# Initial Data Requirements

To use WRFUP effectively, the primary requirement is a geo_em.d0X.nc file for the specific inner domain of the WRF model. This file is generated by the WRF Preprocessing System [@Skamarock2008] using geogrid.exe, following the standard procedure without needing any additional modifications to the namelist.wps file.

In cases where the URB_PARAM or FRC_URB2D fields are missing from the geo_em file, WRFUP automatically creates these fields. It follows the required attributes and structure within the WRF framework to ensure compatibility with urban canopy models.

# Workflow Overview

The entire process for preparing and modifying urban canopy parameters for the Weather Research and Forecasting (WRF) model using WRFUP is handled through a single terminal command. This command allows the user to update the geo_em.d0X.nc file by calculating and ingesting the necessary urban parameters, depending on the specified target (either URB_PARAM or FRC_URB2D). The execution involves running the following command in the CLI (Command Line Interface):

```

wrfup geo_em.d0X.nc URB_PARAM --work_dir YOUR_DIRECTORY

```

or

```

wrfup geo_em.d0X.nc FRC_URB2D --work_dir YOUR_DIRECTORY

```

The tool updates the geo_em file, calculating the urban canopy parameters and generating a new modified output file (e.g., geo_em_URB_PARAM.nc or geo_em_FRC_URB2D.nc), ready for subsequent steps in the WRF modeling workflow.

# Integration in WRF’s Preprocessing

The WRFUP tool is designed to work seamlessly with the Weather Research and Forecasting (WRF) Preprocessing System (WPS). The workflow integrates WRFUP with WRF’s Preprocessing System as shown in Figure 1.

![Integration of WRFUP package within the WRF Preprocessing System workflow. The WRFUP Python package generates a new geo_em file. This file is represented in the figure as geo_em_new.d0X.nc which will typically take the name of geo_em_URB_PARAM.d0X.nc or geo_em_FRC_URB2D.d0X.nc. This file needs to be renamed as the original file to continue the WPS workflow.](figure1.png)

# Important Notes

• Compatibility with WRF Versions: The user should ensure that the WRF version supports the URB_PARAM and FRC_URB2D fields. WRFUP requires WPS version 3.8 or higher for full compatibility with these urban fields and urban parameterization schemes like SLUCM, BEP, and BEP+BEM. Earlier versions may not properly integrate the urban parameters needed for accurate simulations.

• Handling Large Datasets: For large urban areas, it is important to ensure the user’s system has adequate memory and processing power. The tool will always ask for permission to proceed before downloading any dataset.

• Creating and Naming Output Files: After modifying the geo_em files, it is important to adhere to WRF’s naming conventions: renaming the geo_em_URB_PARAM.d0X.nc or geo_em_FRC_URB2D.d0X.nc back to geo_em.d0X.nc before running metgrid.exe in WPS. This will ensure the model’s processing system can fetch the correct file.

• Inspecting Updated URB_PARAM Fields: It is recommended to visually check the correctness of the updated URB_PARAM fields by using visualization tools like xarray or ncview.

• Further Technical Details: For a full breakdown of installation steps, internal structure, and advanced usage scenarios, please refer to the full documentation in Appendix ??.

# References

