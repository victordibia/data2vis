import json
import os
test_dataset_directory = "testdata"


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
                                                       "_")  #remove periods
                        del row[field]
                        row[new_field_name] = field_holder
                with open(filepath, 'w') as outfile:
                    json.dump(data, outfile)


clean_test_dataset_remove_periods()
data = json.load(open(test_dataset_directory + "/boot/aids.json"))
#

# for row in data:
#     for field in row.keys():
#         if (field.contains(".")):
#             print(filepath)
#         field_holder = row[field]
#         new_field_name = field.replace(".", "")  #remove periods
#         del row[field]
#         row[new_field_name] = field_holder

# print(data)