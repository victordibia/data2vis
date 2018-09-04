import os
import json
import matplotlib.pyplot as plt

test_result_dir = "utils/testresults"


def analyze_test_suite(test_dataset_directory):
    for subdir, dirs, files in os.walk(test_dataset_directory):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath.endswith(
                    "json") and not filepath.endswith("lsit.json"):
                data = json.load(open(filepath))
                print(filepath)
                # for row in data:
                #     for field in row.keys():
                #         if "." in field:
                #             print(filepath)
                #         field_holder = row[field]
                #         new_field_name = field.replace(".",
                #                                        "_")  #remove periods
                #         del row[field]
                #         row[new_field_name] = field_holder
                # with open(filepath, 'w') as outfile:
                #     json.dump(data, outfile)


def analyze_data(filepath):
    data = json.load(open("utils/testresults/vizmodelbi15.json"))
    beam_width = data["beamwidth"]
    print(len(data["data"]))
    for data["data"] in row:
        valid_json_count = row["validjsoncount"]
        valid_vega_count = row["validvegacount"]
        phantom_count = row["phantomcount"]


# analyze_test_suite(test_result_dir)

data = json.load(open("utils/testresults/vizmodelbi15.json"))
print(len(data["data"]))