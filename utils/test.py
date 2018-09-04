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
# print(utils.get_test100_data(2))

# # utils.profile_dataset_vegaspec(examples_directory)
# # utils.generate_data_pairs(utils.examples_directory,
# #                           utils.train_data_output_directory,
# #                           utils.data_split_params)

test_data = [{
    "accel": "0.359",
    "dist": "12",
    "event": "1",
    "mag": "7",
    "station": "117"
}]

field_name_types = utils.generate_field_types(test_data)
print(field_name_types, "===\n")

print("Original ====\n", test_data)

forward_norm = utils.replace_fieldnames(test_data, field_name_types, True)
print("Forward ====\n", forward_norm)

back_norm = utils.backward_norm(forward_norm, field_name_types)
print("Backward ====\n", back_norm)

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
