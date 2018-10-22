import os
import json
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats

# t_stat, p_val = stats.ttest_ind(sample1, sample2, equal_var=False)

test_result_dir = "utils/testresults"
all_results = {}
aggregate_terms = [
    "count", "valid", "missing", "distinct", "sum", "mean", "average",
    "variance", "variancep", "stdev", "stdevp", "stderr", "median", "q1", "q3",
    "ci0", "ci1", "min", "max", "argmin", "argmax"
]

file_paths = [
    "/vizmodeluninat5.json", "/vizmodeluninat10.json",
    "/vizmodeluninat15.json", "/vizmodeluninat20.json", "/vizmodeluni5.json",
    "/vizmodeluni10.json", "/vizmodeluni15.json", "/vizmodeluni20.json",
    "/vizmodelbi5.json", "/vizmodelbi10.json", "/vizmodelbi15.json",
    "/vizmodelbi20.json"
]


def analyze_test_suite(test_dataset_directory):
    # for subdir, dirs, files in os.walk(test_dataset_directory):
    #     for file in files:
    #         filepath = subdir + os.sep + file
    #         if filepath.endswith(
    #                 "json") and not filepath.endswith("lsit.json"):
    for filepath in file_paths:
        filepath = test_result_dir + filepath
        # data = json.load(open(filepath))
        # print(filepath)
        analyze_data(filepath)


def is_valid_aggregate(agg_val):
    if (agg_val not in aggregate_terms):
        # print("issh", agg_val)
        return False
    else:
        return True


def computer_anova():
    print("anova")


def analyze_data(filepath):
    data = json.load(open(filepath))
    beam_width = data["beamwidth"]
    valid_json_array = []
    valid_vega_array = []
    phantom_count_array = []
    x = list(range(0, 100))
    for row in data["data"]:
        valid_json_count = row["validjsoncount"] / beam_width
        valid_json_array.append(valid_json_count)
        valid_vega_count = row["validvegacount"]

        vs_array = row["vegaspecarray"]

        # mark specs with incorrect aggregation value as invalid vega
        for vs_row in vs_array:
            if ("aggregate" in vs_row["encoding"]["y"]):
                if not is_valid_aggregate(
                        vs_row["encoding"]["y"]["aggregate"]):
                    valid_vega_count -= 1
                else:
                    if ("aggregate" in vs_row["encoding"]["x"]):
                        if not is_valid_aggregate(
                                vs_row["encoding"]["x"]["aggregate"]):
                            valid_vega_count -= 1

        # print(valid_vega_count, row["validjsoncount"])
        valid_vega_count = valid_vega_count / beam_width
        valid_vega_array.append(valid_vega_count)

        if (valid_vega_count == 0):
            phantom_count = 1
        else:
            phantom_count = row["phantomcount"] / valid_vega_count

        phantom_count_array.append(phantom_count)

    # print(x, valid_json_array)
    # plt.plot(x, valid_json_array)
    # plt.plot(x, valid_vega_array)
    # plt.plot(x, phantom_count_array)
    # plt.show()
    print(
        filepath.split("vizmodel")[1], "Json:",
        round(np.mean(valid_json_array), 3), "Vega",
        round(np.mean(valid_vega_array), 3))
    # "Mean % Phantom",
    # round(np.mean(phantom_count_array), 3))

    result = {"json:": valid_json_array, "vega": valid_vega_array}


analyze_test_suite(test_result_dir)

# data = json.load(open("utils/testresults/vizmodelbi15.json"))
# print(len(data["data"]))
# analyze_data("utils/testresults/vizmodeluninat15.json")
