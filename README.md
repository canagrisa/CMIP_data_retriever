# CMIP Data Retriever

'CMIP_data_retriever' is a Python package that simplifies the process of downloading climate data from the CMIP6 (Coupled Model Intercomparison Project Phase 6) project. It allows users to search for and download the relevant data files from the ESGF (Earth System Grid Federation) repository based on their specific needs and filtering criteria.

## Features

- Specify variables, experiments, models, and other filtering criteria.
- Search for climate data models based on the specified filters.
- Automatically find all models and variants within a module that contain all the selected experiments and variables. This allows for a specific set of variables and scenarios to find all models and variants that can be equally compared to each other.
- Filter models based on the presence of requested variables and experiments.
- Create a pandas DataFrame with an overview of the filtered models, their variants, variables, experiments, and other attributes.
- Save the DataFrame to an Excel file for easy data analysis.
- Download the data files based on the specified filters and filtered models, variants, variables, and experiments.
- Downloads the data in a nested and organized folder structure that eases data retrieval.
- Allows skipping certain models or selecting specific models.
- Optional cropping of the data by a specified region using a polygon.

## Installation

```bash
pip install CMIP_data_retriever
```

## Usage
```python
from cmip_data_retriever import CMIPDownloader

variables = ['variable1', 'variable2']
experiments = ['experiment1', 'experiment2']

downloader = CMIPDownloader(variables=variables, experiments=experiments)

# Save the DataFrame with model information to an Excel file
downloader.save_dataframe(outfolder='output', filename='model_info.xlsx')

# Download the data files
downloader.download_data()
```

## License

MIT License. See the LICENSE file for more information.

## Support and Contributions

For support or to report bugs, please open a GitHub issue. Contributions are welcome! Feel free to submit a pull request or suggest new features by opening an issue.

## Acknowledgments

This package was developed using the PyESGF library to access the ESGF repository.
