import pyesgf
from pyesgf.search import SearchConnection
import os
import pandas as pd
import copy
from . import utils
import xarray as xr
from datetime import datetime

class CMIPDownloader:

    def __init__(self, variables, experiments, model=None, frequency='mon'):

        if isinstance(variables, str):
            variables = [variables]
        if isinstance(experiments, str):
            experiments = [experiments]

        self.experiments = experiments
        self.variables = variables
        self.frequency = frequency
        self.model = model
        self._results = None
        self._models_dict = None
        self._models_dict_filtered = None
        self._df = None

    @property
    def results(self):
        if self._results is None:
            self._results = self.setup_connection()
        return self._results
    
    @property
    def models_dict(self):
        if self._models_dict is None:
            self._models_dict = self.search_models()
        return self._models_dict
    
    @property
    def models_dict_filtered(self):
        if self._models_dict_filtered is None:
            self._models_dict_filtered = self.filter_models()
        return self._models_dict_filtered
    
    @property
    def df(self):
        if self._df is None:
            self._df = self.create_dataframe()
        return self._df
    
    def setup_connection(self):
        """
        Set up a connection to the ESGF server and search for datasets using the
        provided variables, experiments, and other input parameters.
        """

        variables_str = ','.join(self.variables)
        experiments_str = ','.join(self.experiments)

        context_args = {
        'facets': 'project, source_id, experiment_id, variable, frequency, datetime_start, datetime_stop, variant_label, grid_label',
        'latest': True,
        'project': 'CMIP6',
        'variable': variables_str,
        'experiment_id': experiments_str,
        'frequency': self.frequency,
        'grid_label': 'gn,gr',
        # 'index_node': 'esgf-node.llnl.gov'
        }

        if self.model is not None:
            context_args['source_id'] = self.model

        conn = SearchConnection('https://esgf-node.llnl.gov/esg-search', distrib=True)
        query = conn.new_context(**context_args)
        results = query.search()

        def string_to_date(string):
            date = datetime.fromisoformat(string.replace("Z", "+00:00"))
            return date

        def condition_1(result):
            if ('datetime_start' in list(result.json.keys())) and ('datetime_stop' in list(result.json.keys())):
                return True
            else:
                return False

        def condition_2(result):
            if (result.json['experiment_id'][0] in ['ssp126', 'ssp585']):
                if (string_to_date(result.json['datetime_start']).year != 2015) or (string_to_date(result.json['datetime_stop']).year < 2099):
                    return False
                else:
                    return True
            else:
                return True

            
        results = [result for result in results if condition_1(result)]
        results = [result for result in results if condition_2(result)]

        return results
    
    def search_models(self):
        """
        Process the results from the ESGF server and create a nested dictionary
        of models, variants, variables, and experiments.
        """

        models_dict = {}

        # Get a nested dictionary of models, variants, variables, and experiments
        for result in self.results:
            model = result.json['source_id'][0]
            variant = result.json['variant_label'][0]
            variable = result.json['variable'][0]
            experiment = result.json['experiment_id'][0]

            if model not in models_dict:
                models_dict[model] = {}

            if variant not in models_dict[model]:
                models_dict[model][variant] = {}

            if variable not in models_dict[model][variant]:
                models_dict[model][variant][variable] = []

            if experiment not in models_dict[model][variant][variable]:
                models_dict[model][variant][variable].append(experiment)

        models_dict = {key: models_dict[key] for key in sorted(models_dict)}

        return models_dict
    
    def filter_models(self):
        """
        Filter out models that don't have all the requested variables and experiments.
        """

        dic_filt = copy.deepcopy(self.models_dict)

        for model in dic_filt:
            skip_variant_loop = False
            for variant in list(dic_filt[model].keys()):
                skip_variable_loop = False
                if sorted(list(dic_filt[model][variant].keys())) != sorted(self.variables):
                    del dic_filt[model][variant]
                    skip_variant_loop = True
                    continue
                for variable in list(dic_filt[model][variant].keys()):
                    if sorted(dic_filt[model][variant][variable]) != sorted(self.experiments):
                        del dic_filt[model][variant]
                        skip_variable_loop = True
                        break
                    dic_filt[model][variant][variable] = sorted(dic_filt[model][variant][variable])
                if skip_variable_loop:
                    continue
            if skip_variant_loop:
                continue

        dic_filt = {key: value for key, value in dic_filt.items() if len(value) > 0}

        return dic_filt

    def create_dataframe(self):
        """
        Create a DataFrame with information about models, variables, and experiments.
        """

        def get_matching_results(model, variable, experiment):
            return [result for result in self.results if
                    (result.json['source_id'][0] == model) and
                    (result.json['variable'][0] == variable) and
                    (result.json['experiment_id'][0] == experiment) and
                    ('datetime_start' in result.json.keys()) and
                    ('datetime_stop' in result.json.keys())]

        data = []
        models_dict = self.models_dict_filtered

        for model in models_dict:
            num_variants = len(models_dict[model])
            variants = ', '.join(sorted(models_dict[model].keys()))
            first_model_row = True
            for variable in self.variables:
                nominal_resolution = [result.json['nominal_resolution'] for result in self.results if
                                    (result.json['source_id'][0] == model) and (result.json['variable'][0] == variable)][0][0]
                first_variable_row = True
                for experiment in self.experiments:
                    results_match = get_matching_results(model, variable, experiment)

                    size = results_match[0].json['size']
                    date_start = results_match[0].json['datetime_start']
                    date_stop = results_match[0].json['datetime_stop']

                    size = utils.format_size(size)
                    if first_model_row and first_variable_row:
                        data.append([model, num_variants, variants, variable, nominal_resolution, experiment, date_start, date_stop, size])
                    elif first_variable_row:
                        data.append(['', '', '', variable, nominal_resolution, experiment, date_start, date_stop, size])
                    else:
                        data.append(['', '', '', '', '', experiment, date_start, date_stop, size])
                    first_variable_row = False
                first_model_row = False

        df = pd.DataFrame(data, columns=['Model', 'Number of Variants', 'Variants', 'Variables', 'Nominal Resolution', 'Experiments', 'Date Start', 'Date Stop', 'Size'])
        return df
    
    def save_dataframe(self, outfolder=None, filename='model_info.xlsx'):
        """
        Save the DataFrame to an Excel file in the specified output folder with the given filename.
        
        Args:
            outfolder (str, optional): The output folder where the Excel file will be saved. Defaults to the current working directory.
            filename (str, optional): The filename for the Excel file. Defaults to 'model_info.xlsx'.
        """
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        if outfolder is None:
            path = os.path.join(os.getcwd(), filename)      
        else:
            if not os.path.exists(outfolder):
                os.makedirs(outfolder)
            path = os.path.join(outfolder, filename)
            
        self.df.to_excel(path, index=False)

    def download_data(self, model_skip=[], model_select=[], crop_region=None):
        """
        Download data for specified models, variants, variables, and experiments.

        Parameters:
        model_skip (list): A list of model names to skip during the download process. Default is an empty list.

        Returns:
        None
        """

        os.environ['ESGF_PYCLIENT_NO_FACETS_STAR_WARNING'] = '1'

        models = self.models_dict_filtered.keys()

        if len(model_skip) > 0:
            models = [model for model in models if model not in model_skip]

        if len(model_select) > 0:
            models = [model for model in models if model in model_select]

        for model in models:
            for variant in list(self.models_dict_filtered[model].keys())[:5]:
                for variable in self.models_dict_filtered[model][variant]:
                    for experiment in self.models_dict_filtered[model][variant][variable]:
                        print(model, variant, variable, experiment)
                        # Filter results based on model, variant, variable, experiment, and existing datetime keys
                        results_match = [result for result in self.results if
                                        (result.json['source_id'][0] == model) and
                                        (result.json['variant_label'][0] == variant) and
                                        (result.json['variable'][0] == variable) and
                                        (result.json['experiment_id'][0] == experiment)]

                        for _result in results_match:
                            hit = _result.file_context().search()
                            if experiment in ['ssp126', 'ssp585']:
                                files = [{'filename': f.filename, 'url': f.download_url} for f in hit if int(f.filename.split('_')[-1][:4]) >= 2015 
                                            and int(f.filename.split('_')[-1][-11:-7]) <= 2100]
                            else:
                                files = [{'filename': f.filename, 'url': f.download_url} for f in hit]

                            if len(files) > 0:
                                
                                ofo = f'../data/CMIP6/{model}/{variant}/{variable}/{experiment}/'
                                
                                # Create the output directory if it does not exist
                                if not os.path.exists(ofo):
                                    os.makedirs(ofo)
                                
                                files = pd.DataFrame.from_dict(files)
                                
                                # Download the files if they do not already exist in the output directory
                                for index, row in files.iterrows():
                                    path = ofo + row.filename
                                    path_crop = path.replace('.nc', f'_{crop_region}_crop.nc')
                                    if os.path.isfile(path) or os.path.isfile(path_crop):
                                        print("File exists. Skipping.")
                                    else:
                                        utils.download(row.url, path)
                                        if crop_region is not None:
                                            ds = xr.open_dataset(path)
                                            ds_crop = utils.crop_by_polygon(ds, polygon=crop_region)
                                            ds_crop.to_netcdf(path_crop)
                                            os.remove(path)
                                break
