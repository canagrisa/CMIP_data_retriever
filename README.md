[![DOI](https://zenodo.org/badge/627657760.svg)](https://zenodo.org/badge/latestdoi/627657760)

# CMIP Data Retriever

The 'CMIP_data_retriever' is an easy-to-use Python package designed to streamline the process of obtaining climate data from the CMIP6 (Coupled Model Intercomparison Project Phase 6) initiative. By providing a seamless interface with the ESGF (Earth System Grid Federation) repository, users can effortlessly search for and download pertinent data files tailored to their specific requirements and filter preferences.

This package's primary function is to automatically identify and download all relevant models and variants that meet a common set of criteria. For instance, by inputting a selection of experiments (e.g., 'SSP1-2.6', 'SSP5-8.5'), variables (e.g., 'tos' and 'tas'), grid type (e.g., native grid), and frequency (e.g., monthly), users can easily search for all models and variants containing data that match all of these specifications and readily download them in a structured nested folder structure. This functionality aims to simplify the process of working with a robust ensemble of models that share specifications.

Information about the model varialbes can be found in https://pcmdi.llnl.gov/mips/cmip3/variableList.html.

## Features

- Search for climate data models based on variables, experiments, models, and other filtering criteria like frequency, grid type, etc.
- Automatically find all models and variants within a module that contain all the selected experiments and variables. 
- Create a pandas DataFrame with an overview of the models, their variants, variables, experiments, and other attributes.
- Save the DataFrame to an Excel file for easy data analysis.
- Download the data files in a nested and organized folder structure based on the specified filters and filtered models, variants, variables, and experiments.
- Optional cropping of the data by a specified region using a polygon.

## Installation

```bash
pip install git+https://github.com/canagrisa/CMIP_data_retriever.git
```

## Usage
```python
from cmip_data_retriever import CMIPDownloader

# Select the scenarios of interest
scenarios = ['historical', 'ssp126', 'ssp585']

# Select the variables of interest (surface air temperature and precipitation in this case)
variables = ['tas', 'pr']

# Select the frequency (monthly, in this case)
frequency = 'mon'

# Select the grid type (native grid, in this case)
grid_type = 'gn'

# Initialize the CMIPDownloader class and find the data (this may take a few minutes)
downloader = CMIPDownloader(scenarios=scenarios, variables=variables, frequency=frequency, grid=grid_type)

# Get a simple dictionary with the models and variants found. This dictionary will mimic the folder structure when downloading.
models = downloader.models_dict_filtered
print(list(models.keys()))

# Create a DataFrame with model information
model_info_df = downloader.create_dataframe()

# Save the DataFrame with model information to an Excel file
downloader.save_dataframe(output_folder='path/to/folder', filename='model_info.xlsx')

# Define the polygonal region to be cropped, delimiting the Mediterranean Sea in this case.
region =  [(-6, 30), (-5.31, 41), (13.66, 47.29), (26.80, 41.43), (27.08, 40.05), (39, 38.2), (36, 30)]

# Download the data files (in this case, for the first 2 models found)
# Crop for the region specified by the polygon.
# Set the maximum number of variants to be downloaded for each model (4 in this case). Some models have up to 40 variants, so it's a good idea to set a limit if necessary.
downloader.download_data(model_select=models[:2], destination_folder='path/to/folder/', crop_region=region, max_variants=4)

# The .download_data() method has 'model_select' and 'model_skip' arguments, which default to None. If not provided, all models are downloaded.

```

## Example


Example of download results from the usage example below
![fig_1](/home/prossello/CMIP_data_retriever/data/rec.gif)


## License

MIT License. See the LICENSE file for more information.

## Support and Contributions

For support or to report bugs, please open a GitHub issue. Contributions are welcome! Feel free to submit a pull request or suggest new features by opening an issue.

## Acknowledgments

This package was developed using the PyESGF library to access the ESGF repository.
