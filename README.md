# CMIP Data Retriever

'CMIP_data_retriever' is a Python package that simplifies the process of downloading climate data from the CMIP6 (Coupled Model Intercomparison Project Phase 6) project. It allows users to search for and download the relevant data files from the ESGF (Earth System Grid Federation) repository based on their specific needs and filtering criteria.

## Features

- Search for climate data models based on variables, experiments, models, and other filtering criteria.
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

variables = ['variable1', 'variable2']
experiments = ['experiment1', 'experiment2']

downloader = CMIPDownloader(variables=variables, experiments=experiments)

# Save the DataFrame with model information to an Excel file
downloader.save_dataframe(outfolder='output', filename='model_info.xlsx')

# Download the data files and crop for the Mediterranean Sea
downloader.download_data(crop_region='med')
```

## License

MIT License. See the LICENSE file for more information.

## Support and Contributions

For support or to report bugs, please open a GitHub issue. Contributions are welcome! Feel free to submit a pull request or suggest new features by opening an issue.

## Acknowledgments

This package was developed using the PyESGF library to access the ESGF repository.
