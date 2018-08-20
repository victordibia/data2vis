import json
import os
import operator
test_dataset_directory = "testdata"
import data_utils as utils

examples_directory = "examples"
train_data_path = "examplesdata/"
test_data_path = "testdata/"

# utils.get_train_dataset_properties(train_data_path)
# utils.get_test_dataset_properties(test_data_path)
print(utils.get_test100_data(2))

# # utils.profile_dataset_vegaspec(examples_directory)
# # utils.generate_data_pairs(utils.examples_directory,
# #                           utils.train_data_output_directory,
# #                           utils.data_split_params)

# test_data = [{
#     "Al": "231",
#     "Ba": "13.2",
#     "Br": "8",
#     "Ca": "3602",
#     "Ce": "0.92",
#     "Cu": "0.3",
#     "Dy": "0.14",
#     "Er": "0.1",
#     "Fe": "944",
#     "Gd": "0.18",
#     "Ho": "0.04",
#     "K": "230",
#     "La": "0.55",
#     "Li": "0.6",
#     "Mg": "828",
#     "Mn": "2.18",
#     "Nd": "0.76",
#     "Pr": "0.18",
#     "Rb": "0.58",
#     "River1": "Grasse1",
#     "River2": "Grasse2",
#     "River3": "Grasse3",
#     "River4": "Grasse4",
#     "River5": "Grasse5",
#     "Si": "3482",
#     "Site": "1",
#     "Sr": "19.35",
#     "Y": "1.15",
#     "Yb": "0.1",
#     "Zn": "10",
#     "Zr": "0.1"
# }]

# field_name_types = utils.generate_field_types(test_data)
# print(field_name_types, "===\n")

# # def fname_dict_to_array(field_name_types):
# #     fname_array = []
# #     for fname in field_name_types:
# #         fname_array.append({fname: field_name_types[fname]})

# #     return list(reversed(fname_array))

# def replace_fieldnames(source_data, field_name_types, replace_direction):
#     for field_name in field_name_types:
#         # print(field_name)
#         field = list(field_name.keys())[0]
#         value = field_name[field]
#         print(field, value)

#         if (replace_direction):
#             source_data = str(source_data).replace(str(field), value)
#         else:
#             source_data = str(source_data).replace(str(value), field)
#     return source_data

# replaced = replace_fieldnames(test_data, field_name_types, True)
# print(replaced)
# # for field_name in fname_dict_to_array(field_name_types):
# #     field = list(field_name.keys())[0]
# #     value = field_name[field]
# #     print(field, value)
