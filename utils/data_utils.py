# Data processing script for vega sample files
import json
import os
from random import randint, shuffle
import csv
from dateutil.parser import parse
import matplotlib.pyplot as plt
from collections import Counter
import operator

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

data_prefix = "examplesdata/"
examples_directory = "examples"
vl_data_filename = "examples/vldata.json"
test_dataset_directory = "testdata"

test_data_list = "testdata/tdatalsit.json"

train_data_output_directory = "sourcedata"
max_file_size = 1219853
max_testdata_file_size = 59853
max_data_slice_size = 20
datapair_slice_size = 1

max_test_data_length = 150
max_source_seq_length = 0
max_target_seq_length = 0

num_samples_per_example = 50

data_split_params = [{
    "tag": "train",
    "percentage": [0, 0.8]
}, {
    "tag": "dev",
    "percentage": [0.8, 0.9]
}, {
    "tag": "test",
    "percentage": [0.9, 1]
}]

test_100_file_path = "utils/testlist.json"

test_100_list = json.load(open(test_100_file_path))


# Shuffle elements in an array according to given order
def shuffle_elements(rand_order, source_list):
    result_list = []
    for r_order in rand_order:
        result_list.append(source_list[r_order])

    return result_list


# inspect variable type float
def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True


# inspect variable type int
def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b


def is_date(string):
    if isint(string) or isfloat(string):
        return False
    try:
        # print(string)
        parse(string)
        return True
    except ValueError:
        return False


"""[Check other members of the array to learn field type]
Returns:
    [type] -- [description]
"""


def non_null_label(full_array, label_key):
    result_val = 0
    for row in full_array:
        if (row[label_key] is not None):
            result_val = row[label_key]
            return result_val
        else:
            result_val = 0
    return result_val


# Generate an array of field types for a given dataset
def generate_field_types(t_data):
    # print (t_data[0])
    data_labels = {"str": 0, "num": 0, "dt": 0}
    field_name_types = {}
    field_name_types_array = []
    for field_name in t_data[0]:
        current_label = non_null_label(t_data,
                                       field_name)  # t_data[0][field_name]
        # print("=====", current_label, field_name)
        if (is_date(current_label) and not (isint(current_label)) and not (isfloat(current_label))):
            replace_num_var = "dt" + str(data_labels["dt"])
            data_labels["dt"] = data_labels["dt"] + 1
            field_name_types[field_name] = replace_num_var
            field_name_types_array.append({field_name: replace_num_var})
        elif (isint(current_label) or isfloat(current_label)):
            replace_num_var = "num" + str(data_labels["num"])
            data_labels["num"] = data_labels["num"] + 1
            field_name_types[field_name] = replace_num_var
            field_name_types_array.append({field_name: replace_num_var})
        else:
            replace_str_var = "str" + str(data_labels["str"])
            data_labels["str"] = data_labels["str"] + 1
            field_name_types[field_name] = replace_str_var
            field_name_types_array.append({field_name: replace_str_var})
    # print(field_name_types_array)
    return list(reversed(field_name_types_array))


# Replace field names with normalized strings based on field type
# replace_direction true = forward norm ... from json to normalized
def replace_fieldnames(source_data, field_name_types, replace_direction):
    # for field_name in field_name_types:
    #     if (replace_direction):
    #         source_data = str(source_data).replace(
    #             str(field_name), field_name_types[field_name])
    #     else:
    #         source_data = str(source_data).replace(
    #             str(field_name_types[field_name]), field_name)
    # return source_data
    for field_name in field_name_types:
        # print(field_name)
        field = list(field_name.keys())[0]
        value = field_name[field]
        # print(field, value)

        if (replace_direction):
            source_data = str(source_data).replace(str(field), value)
        else:
            source_data = str(source_data).replace(str(value), field)
    return source_data


"""[Generate a training data key pair for seq2seq model ]
Source: 3 random data points sampled from the dataset for each vegaspec
target: a valid vegalite spec for the sampled data
Note: the data portion of the vegalite spec is replaced with an empty space

"""


def generate_data_pairs(examples_directory, train_data_output_directory,
                        data_split_params):
    all_sources_hold = []
    all_target_hold = []

    max_source_seq_length = 0
    max_target_seq_length = 0

    print("Generating source and target pairs ======")
    for subdir, dirs, files in os.walk(examples_directory):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith("vl.json"):
                data = json.load(open(filepath))

                if ("url" in data["data"]):

                    data_file_url = data_prefix + data["data"]["url"].rsplit(
                        '/', 1)[-1]
                    del data["_info"]
                    if ("_any" in data["encoding"]):
                        del data["encoding"]["_any"]
                    del data["data"]
                    del data["config"]

                    if ("x" in data["encoding"]
                            and "scale" in data["encoding"]["x"]):
                        # print(data["encoding"]["x"]["scale"])
                        del data["encoding"]["x"]["scale"]

                    if ("y" in data["encoding"]
                            and "scale" in data["encoding"]["y"]):
                        # print("y", data["encoding"]["y"]["scale"])
                        del data["encoding"]["y"]["scale"]

                    target_vega_spec = str(json.dumps(data))
                    target_vega_spec = target_vega_spec.replace(
                        ', "_any": false', '')

                    # keep track of max targe sequence length
                    if len(target_vega_spec) > max_target_seq_length:
                        max_target_seq_length = len(target_vega_spec)

                    data_content = json.load(open(data_file_url))
                    # print("Content lenght", len(data_content), data_file_url)
                    data_holder = []
                    for i in range(0, datapair_slice_size):
                        selected_index = randint(0, len(data_content) - 1)
                        data_holder.append(data_content[selected_index])
                    source_data_spec = str(json.dumps(data_holder))

                    # Generate field name types
                    t_data = data_content
                    # # print (t_data[0])
                    # data_labels = {"str":0,"num":0}
                    # field_name_types = {}
                    field_name_types = generate_field_types(t_data)

                    # Sample each example file a few times
                    for i in range(0, num_samples_per_example):
                        data_holder = []
                        for i in range(0, datapair_slice_size):
                            selected_index = randint(0, len(data_content) - 1)
                            data_holder.append(data_content[selected_index])
                        source_data_spec = str(json.dumps(data_holder))

                        # Replace filednames with normalized string and norm values
                        target_vega_spec = replace_fieldnames(
                            target_vega_spec, field_name_types, True)
                        source_data_spec = replace_fieldnames(
                            source_data_spec, field_name_types, True)
                        # for field_name in field_name_types:
                        #     target_vega_spec = target_vega_spec.replace(
                        #         str(field_name), field_name_types[field_name])
                        #     source_data_spec = source_data_spec.replace(
                        #         str(field_name), field_name_types[field_name])

                        # print(source_data_spec, "=****=", target_vega_spec,
                        #       "==========\n")

                        # Keep track of maximum source sequence length
                        if len(source_data_spec) > max_source_seq_length:
                            max_source_seq_length = len(source_data_spec)

                        all_sources_hold.append(source_data_spec)
                        all_target_hold.append(target_vega_spec)
                    # break

    with open(
            train_data_output_directory + "/all_train.sources",
            mode='wt',
            encoding='utf-8') as outfile:
        outfile.write('\n'.join(str(line) for line in all_sources_hold))
    with open(
            train_data_output_directory + "/all_train.targets",
            mode='wt',
            encoding='utf-8') as outfile:
        outfile.write('\n'.join(str(line) for line in all_target_hold))

    print("size of all files", len(all_sources_hold), len(all_target_hold))
    print("Max Source Seq Lenght", max_source_seq_length)
    print("Max Target Seq Lenght", max_target_seq_length)

    # Uniformly shuffle source and target sequence pair lists
    rand_list = list(range(0, len(all_sources_hold) - 1))
    shuffle(rand_list)
    # print(rand_list)
    all_sources_hold = shuffle_elements(rand_list, all_sources_hold)
    all_target_hold = shuffle_elements(rand_list, all_target_hold)

    for param in data_split_params:
        with open(
                train_data_output_directory + "/" + param["tag"] + ".sources",
                mode='wt',
                encoding='utf-8') as outfile:
            outfile.write('\n'.join(
                str(line) for line in all_sources_hold[int(
                    param["percentage"][0] * len(all_sources_hold)):int(
                        param["percentage"][1] * len(all_sources_hold))]))
        print("  > Saved ",
              train_data_output_directory + "/" + param["tag"] + ".sources")
        with open(
                train_data_output_directory + "/" + param["tag"] + ".targets",
                mode='wt',
                encoding='utf-8') as outfile:
            outfile.write('\n'.join(
                str(line) for line in all_target_hold[int(
                    param["percentage"][0] * len(all_target_hold)):int(
                        param["percentage"][1] * len(all_target_hold))]))
        print("  > Saved ",
              train_data_output_directory + "/" + param["tag"] + ".targets")


"""[Delete none vl spec files from examples directory, generate a list of datafiles]
"""


def clean_examples_directory(examples_directory):
    print(
        "Cleaning example files. Removing png, csv and other file types from example directory."
    )
    vl_data_list = []
    for subdir, dirs, files in os.walk(examples_directory):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith("vl.json"):
                # print (filepath)
                vl_data_list.append(filepath)
            else:
                os.remove(filepath)

    with open(vl_data_filename, 'w') as outfile:
        print("writing vldata.json to file")
        json.dump(vl_data_list, outfile)
    # stuff_in_data()
    print("Example file cleaning complete.")


# Read CSV File
def read_csv(file, json_file, format):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        title = reader.fieldnames
        for row in reader:
            csv_rows.extend(
                [{title[i]: row[title[i]]
                  for i in range(len(title))}])
        write_json(csv_rows, json_file, format)


# Convert csv data into json and write it
def write_json(data, json_file, format):
    with open(json_file, "w") as f:
        if format == "pretty":
            f.write(
                json.dumps(
                    data,
                    sort_keys=False,
                    indent=4,
                    separators=(',', ': '),
                    encoding="utf-8",
                    ensure_ascii=False))
        else:
            f.write(json.dumps(data))


"""[Transform CSV datafiles into json.. to have a unified dataformat that RNN can learn from]
"""


def transform_csv_json(csv_directory, delete_after_convert):
    for subdir, dirs, files in os.walk(csv_directory):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith("csv"):
                read_csv(filepath, filepath.replace("csv", "json"), format)
                if (delete_after_convert):
                    os.remove(filepath)


def get_train_dataset_properties(train_data_path):
    data_used = [
        "population.json", "movies.json", "jobs.json", "iris.json",
        "driving.json", "crimea.json", "cars.json", "weball26.json",
        "burtin.json", "barley.json", "birdstrikes.json"
    ]
    property_holder = []
    for datafile in data_used:
        filepath = train_data_path + datafile
        data_content = json.load(open(filepath))
        # print("Num columns:", (data_content[0]), filepath)
        for row in data_content:
            print(filepath, len(row))
            property_holder.append(len(row))
            break
    print("mean: ",
          sum(property_holder) / len(row), " min", min(property_holder),
          " max", max(property_holder))


def get_test100_data(index):
    data = json.load(open(test_100_list[index]))

    return data


def get_test_dataset_properties(test_data_path):
    property_holder = []
    list_holder = []
    for subdir, dirs, files in os.walk(test_data_path):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith("json"):
                data_content = json.load(open(filepath))
                for row in data_content:
                    if (len(row) > 4 and len(row) < 7):
                        # print(filepath, len(row))
                        property_holder.append(len(row))
                        list_holder.append(filepath)
                    break
    print("Num valunes", len(property_holder), "mean: ",
          sum(property_holder) / len(row), " min", min(property_holder),
          " max", max(property_holder))

    with open(test_100_file_path, 'w') as outfile:
        json.dump(list_holder[:100], outfile)


"""[Reduce datset size to a threshold. Also delete datasets with less than 7 items ... 
   they usually have non-standard fields/structure that may disrupt learning]
"""


def reduce_dataset_size():
    for subdir, dirs, files in os.walk(data_prefix):
        for file in files:
            filepath = subdir + file
            if filepath.endswith("json"):
                data_content = json.load(open(filepath))
                if (len(data_content) < 7):
                    os.remove(filepath)
                data_holder = []
                i = 0
                for item in data_content:
                    data_holder.append(item)
                    if (i > max_data_slice_size):
                        break
                    i = i + 1
                print("=======", filepath, len(data_content),
                      max_data_slice_size)
                with open(filepath, 'w') as outfile:
                    json.dump(data_holder, outfile)

            else:
                os.remove(filepath)


def load_test_dataset():
    if not (os.path.exists(test_data_list)):
        print("Test data list does not exists. Creating it now at",
              test_data_list)
        file_list = []
        for subdir, dirs, files in os.walk(test_dataset_directory):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith("json"):
                    file_list.append(filepath)
                    print(filepath)
        with open(test_data_list, 'w') as outfile:
            print("writing test data file list to file")
            json.dump(file_list, outfile)

    all_json_files = json.load(open(test_data_list))
    # print("Selecting a dataset at random from ", len(all_json_files))
    data = json.load(open(all_json_files[randint(0, len(all_json_files) - 1)]))
    return (data)


# process test dataset. Remove periods from field names. Vegalite fails if
# field names contain periods. This makes Data2Vis look bad.


def clean_test_dataset_remove_periods():
    for subdir, dirs, files in os.walk(test_dataset_directory):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(
                    "json") and not filepath.endswith("lsit.json"):
                data = json.load(open(filepath))
                for row in data:
                    for field in row.keys():
                        if "." in field:
                            print(filepath)
                        field_holder = row[field]
                        new_field_name = field.replace(".",
                                                       "_")  # remove periods
                        del row[field]
                        row[new_field_name] = field_holder
                with open(filepath, 'w') as outfile:
                    json.dump(data, outfile)


# Perform preprocessing on dataset used to test predictions.
def clean_test_dataset():
    for subdir, dirs, files in os.walk(test_dataset_directory):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(
                    "json") and not filepath.endswith("lsit.json"):
                data = json.load(open(filepath))

                # delete empy datasets
                if (len(data) == 0):
                    print("====== Deleting: Empty Dataset ========")
                    os.remove(filepath)
                else:
                    # delete datasets with less than 4 fields
                    first_row = data[0]
                    if (len(first_row) < 4):
                        print("====== Deleting: less than 4 fields ========")
                        os.remove(filepath)
                    else:
                        for row in data:
                            if ("" in row):
                                del row[""]
                            if ("default" in row):
                                del row["default"]

                        if (len(data) > max_test_data_length):
                            print("File has more than ", max_test_data_length,
                                  " elements. Reducing ..")
                            data = data[:max_test_data_length]
                        with open(filepath, 'w') as outfile:
                            json.dump(data, outfile)

                        # remove large files
                        data_file_size = os.path.getsize(filepath)
                        if (data_file_size > max_testdata_file_size):
                            print(
                                "Data file greater than max. Deleting Example",
                                data_file_size)
                            os.remove(filepath)
                        # save only a fraction of data to reduce load time in demo


def get_count_freqs(input_array):
    counted_marks = (Counter(input_array))
    counted_marks = list(sorted(counted_marks.items()))
    counts_marks = []
    freqs_marks = []
    for row in counted_marks:
        counts_marks.append(row[1])
        freqs_marks.append(row[0])
    return (counts_marks, freqs_marks)


# Generate some statistics on source dataset
def profile_dataset_vegaspec(examples_directory):
    mark_types = []
    transformation_types = [
        "bin", "aggregate", "calculate", "filter", "timeUnit", "sort"
    ]
    transform_counts = []
    for subdir, dirs, files in os.walk(examples_directory):
        for file in files:
            filepath = os.path.join(subdir, file)
            if filepath.endswith("vl.json"):
                data = json.load(open(filepath))
                mark_types.append(data["mark"])
                data_string = str(data)
                for transform_val in transformation_types:
                    if (transform_val in data_string):
                        transform_counts.append(transform_val)

    counts_marks, freqs_marks = get_count_freqs(mark_types)

    plt.figure(figsize=(8, 3))
    plt.subplot(1, 2, 1)
    plt.bar(freqs_marks, counts_marks)
    # plt.hist(counted_marks)

    counts_transform, freqs_transform = get_count_freqs(transform_counts)
    print(counts_transform, freqs_transform)

    plt.subplot(1, 2, 2)
    plt.bar(freqs_transform, counts_transform)
    # fig = plt.figure(figsize=(8, 4))
    plt.savefig(
        'docs/datasetcharacteristics.eps',
        format='eps',
        dpi=1000,
        bbox_inches='tight')
    # plt.show()
    print("Total examples", len(mark_types))
    # plt.show()


def write_data_to_file(destination_file, source_data_first_sample):
    # Write normalized JSON to file for seq2seq model
    # print("Writing data to file:", source_data_first_sample)
    with open(destination_file, 'w') as source_data_file:
        json.dump(source_data_first_sample, source_data_file)
        # source_data_file.write((json.dumps(source_data)))


# Normalize source json data fieldnames before visualization prediction
def forward_norm(source_data, destination_file, f_names):

    source_data_first_sample = source_data[0]
    source_data_first_sample = replace_fieldnames(source_data_first_sample,
                                                  f_names, True)
    source_data_first_sample = source_data_first_sample.replace("'", '"')
    # print("************",  source_data_first_sample )

    try:
        source_data_first_sample = json.loads(source_data_first_sample)
    except JSONDecodeError as e:
        return False

    # Write normalized JSON to file for seq2seq model
    # print("Writing data to file:", source_data_first_sample)
    write_data_to_file(destination_file, source_data_first_sample)
    # with open(destination_file, 'w') as source_data_file:
    #     json.dump(source_data_first_sample, source_data_file)
    #     # source_data_file.write((json.dumps(source_data)))
    return True


# Normalize output data after prediction ... replace short values with actual field names
def backward_norm(decoded_string, f_names):
    return replace_fieldnames(decoded_string, f_names, False)


def save_test_results(input_data):
    saved_result_path = "utils/testresults/" + input_data["model"] + str(
        input_data["beamwidth"]) + ".json"
    with open(saved_result_path, 'w') as outfile:
        print("writing test results to file")
        json.dump(input_data, outfile)
