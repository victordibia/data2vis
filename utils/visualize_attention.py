import numpy as np
import pickle
from matplotlib import pyplot as plt
import matplotlib.ticker as ticker
"""
This script helps generate plots from saved attention scores.
Scores are saved in the attention_scores_path variable.
"""

attention_scores_path = "attention_plot/attention_scores.pkl"


def _get_prediction_length(predictions_dict):
    """Returns the length of the prediction based on the index
  of the first SEQUENCE_END token.
  """
    tokens_iter = enumerate(predictions_dict["predicted_tokens"])
    return next(((i + 1) for i, _ in tokens_iter if _ == "SEQUENCE_END"),
                len(predictions_dict["predicted_tokens"]))


def _create_figure(predictions_dict):
    """Creates and returns a new figure that visualizes
  attention scores for for a single model predictions.
  """

    # Find out how long the predicted sequence is
    target_words = list(predictions_dict["predicted_tokens"])

    prediction_len = _get_prediction_length(predictions_dict)

    # Get source words
    source_len = predictions_dict["features.source_len"]
    source_words = predictions_dict["features.source_tokens"][:source_len]

    # Plot
    plot_data = predictions_dict["attention_scores"][:prediction_len, :
                                                     source_len]
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)

    ax.matshow(plot_data, cmap='Blues')
    fontdict = {'fontsize': 14}

    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

    print("".join([str(row) for row in source_words]).replace(
        "SEQUENCE_END", ""))
    print("========")
    print("".join([str(row) for row in target_words]).replace(
        "SEQUENCE_END", ""))

    #   print(source_words.join(""), " >>>>>>>>>>" , target_words.join(""))

    #   ax.set_xticklabels([''] + source_words, fontdict=fontdict, rotation=90)
    #   ax.set_yticklabels([''] + target_words, fontdict=fontdict)

    #   fig = plt.figure(figsize=(8, 8))
    #   plt.imshow(
    #       X=predictions_dict["attention_scores"][:prediction_len, :source_len],
    #       interpolation="nearest",
    #       cmap=plt.cm.Blues)
    plt.xticks(np.arange(source_len), source_words, rotation=90)
    plt.yticks(np.arange(prediction_len), target_words, rotation=0)
    #   fig.tight_layout()

    plt.show()


with open("attention_plot/attention_scores.pkl", 'rb') as f:
    attention_plot = pickle.load(f)
    _create_figure(attention_plot)
