# LAI_modeling_based_on_vegetation_types
LAI modeling based on vegetation types

## Table of Contents

1. [Description](#description)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Usage Examples](#usage-examples)
5. [Project Structure](#project-structure)
6. [License](#license)
7. [Contact](#contact)

## Description

This project is designed for processing LAI (Leaf Area Index) data and generating new raster images  
 based on input vegetation data for the base period and predicted data.  

The project takes raw LAI data for the base period, which is then converted into a more accessible  
format for further use. Using base period vegetation type data and forecasted data, it generates  
new rasters with normalized LAI values for the forecast period.  

Depending on the requirements, the results may include:  

- CSV files containing statistical data on LAI values broken down by day and vegetation class.  
- PNG files with graphs showing average LAI values for each studied year.  
- Rasters containing normalized LAI values for the forecasted period.  

## Requirements

- List of software and packages required to run the project:
  - Python 3.9+
  - geopandas
  - numpy
  - pandas
  - rasterio
  - matplotlib

## Installation

Instructions for setting up the project. Example:

1. Clone the repository:
    ```bash
    git clone https://github.com/IvanShkvyr/LAI_modeling_based_on_vegetation_types
    ```
2. Navigate to the project directory:
    ```bash
    cd LAI_modeling_based_on_vegetation_types
    ```
3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage Examples

Examples of code or commands that show how to use the project.

```python
# Usage example
from data_processing import process_lai_modeling, plot_lai_by_plants


"""
Data for the function process_lai_modeling
"""
# Path to the file containing raw vegetation data for the year 2020
vegetation_file_path = "..."

# Path to the file containing raw vegetation data for the predict year
predicted_vegetation = "..."

# Path to the folder with raw LAI data for the year 2020
lai_dir = "..."

# Path to shapefile containing the boundary of the study area
shapefile_path = "..."


"""
Data for the function plot_lai_by_plants
"""
# Path to the file containing vegetation data for the forecast year
vegetation_predict_path = "..."

# Path to the folder with forecasted LAI data for the projected period
lai_folder_predict_path = "..."

# Path to the file containing vegetation data for the year 2020
# File after normalization (contains data following the execution of the first function)
vegetation_base_path = "..."

# Path to the folder with normalized LAI data for the year 2020
lai_folder_base_path = "..."

# Path to shapefile containing the boundary of the study area
shapefile_path = "..."

process_lai_modeling(
    vegetation_map_path=vegetation_file_path,s
    predicted_vegetation_dir=predicted_vegetation,
    lai_daily_avg_dir=lai_dir,
    study_area_shapefile=shapefile_path
)


plot_lai_by_plants(
                vegetation_predict=vegetation_predict_path,
                lai_folder_predict=lai_folder_predict_path,
                vegetation_base=vegetation_base_path,
                lai_folder_base=lai_folder_base_path,
                study_area_shapefile=shapefile_path
                )

```

## Project Structure 

lai_data_processing_project/  
│  
├── lai_data_processing/           # Main module  
│   ├── __init__.py  
│   ├── data_processing.py  
│   ├── file_management.py  
│   ├── main.py  
│   ├── plotting.py  
│   └── raster_processing.py  
│  
├── LICENSE               # Licence file 
├── README.md             # Description file (this file)  
├── requirements.txt      # List of dependencies  
└── setup.py              # Installation script  

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for more details.

## Contact
If you have any questions or suggestions, you can contact me at:

Name: Ivan Shkvyr (GIS spetialist in CzeckGlobe)
Email: shkvyr.i@czechglobe.cz

