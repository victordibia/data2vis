
import data_utils
import json
 

# Generate training data splits. 
# input source_directory - path to directory containing vegalite examples
        # data_split_params - train/text/dev data split configuration
        # output_directory - path to directory containing generated train/dev/test source files and vocabularies

source_directory = "examples"
data_split_params = [{"tag": "train","percentage":[0,0.8]},{"tag": "dev","percentage":[0.8,0.9]},{"tag": "test","percentage":[0.9,1]}]
output_directory = "sourcedata"
data_utils.generate_data_pairs(source_directory,output_directory, data_split_params)