#! /usr/bin/env python
# C

#
""" Webserver to load predictions and serve over http endpoints
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from pydoc import locate
import json
import yaml
from six import string_types

from utils import data_utils
import argparse

from flask import Flask, render_template, request, jsonify

import tensorflow as tf
from tensorflow import gfile
from flask_cors import CORS, cross_origin

from seq2seq import tasks, models
from seq2seq.configurable import _maybe_load_yaml, _deep_merge_dict
from seq2seq.data import input_pipeline
from seq2seq.inference import create_inference_graph
from seq2seq.training import utils as training_utils

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

app = Flask(__name__, )
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
predictions = None

PARSER = argparse.ArgumentParser(description="Generates toy datasets.")
PARSER.add_argument(
    "--port", type=int, default=5016, help="Specify port number to run demo")
PARSER.add_argument(
    "--dump_attention", type=int, default=0, help="Dump attention to file")
PARSER.add_argument(
    "--model_dir",
    type=str,
    default="vizmodel",
    help="Specify which directory contains your trained model.")
PARSER.add_argument(
    "--beam_width", type=int, default=15, help="Beam width", required=False)
ARGS = PARSER.parse_args()

destination_file = "test.txt"
# Setup Input parameters
input_pipeline_dict = {
    'class': 'ParallelTextInputPipeline',
    'params': {
        'source_delimiter': '',
        'target_delimiter': '',
        'source_files': [destination_file]
    }
}

model_dir_input = ARGS.model_dir

input_task_list = [{'class': 'DecodeText', 'params': {'delimiter': ''}}]

dump_attention_task = {
    'class': 'DumpAttention',
    'params': {
        'dump_plots': False,
        'output_dir': "attention_plot"
    }
}

# add dump attention task if we have only a single result.
if (ARGS.beam_width == 1 and ARGS.dump_attention == 1):
    input_task_list.append(dump_attention_task)

#  {'class': 'DumpBeams', 'params': {'file': ['out.npz']}}]
model_params = "{'inference.beam_search.beam_width': 5}"
batch_size = 32
loaded_checkpoint_path = None

session_creator = None
hooks = []
decoded_string = ""


def ensure_str(s):
    if isinstance(s, str):
        s = s.encode('utf-8')
    return s


fl_tasks = _maybe_load_yaml(str(input_task_list))
fl_input_pipeline = _maybe_load_yaml(str(input_pipeline_dict))

# Load saved training options
train_options = training_utils.TrainOptions.load(model_dir_input)

# Create the model
model_cls = locate(train_options.model_class) or \
    getattr(models, train_options.model_class)
model_params = train_options.model_params
if (ARGS.beam_width != 1):
    model_params["inference.beam_search.beam_width"] = ARGS.beam_width
model_params = _deep_merge_dict(model_params, _maybe_load_yaml(model_params))
model = model_cls(params=model_params, mode=tf.contrib.learn.ModeKeys.INFER)

print("========model params ==========", model_params)


def _handle_attention(attention_scores):
    print(">>> Saved attention scores")


def _save_prediction_to_dict(output_string):
    global decoded_string
    decoded_string = output_string


# Load inference tasks
for tdict in fl_tasks:
    if not "params" in tdict:
        tdict["params"] = {}
    task_cls = locate(str(tdict["class"])) or getattr(tasks, str(
        tdict["class"]))
    if (str(tdict["class"]) == "DecodeText"):
        task = task_cls(
            tdict["params"], callback_func=_save_prediction_to_dict)
    elif (str(tdict["class"]) == "DumpAttention"):
        task = task_cls(tdict["params"], callback_func=_handle_attention)

    hooks.append(task)

input_pipeline_infer = input_pipeline.make_input_pipeline_from_def(
    fl_input_pipeline,
    mode=tf.contrib.learn.ModeKeys.INFER,
    shuffle=False,
    num_epochs=1)

# Create the graph used for inference
predictions, _, _ = create_inference_graph(
    model=model, input_pipeline=input_pipeline_infer, batch_size=batch_size)

graph = tf.get_default_graph()


# Function to run inference.
def run_inference():
    # tf.reset_default_graph()
    with graph.as_default():
        saver = tf.train.Saver()
        checkpoint_path = loaded_checkpoint_path
        if not checkpoint_path:
            checkpoint_path = tf.train.latest_checkpoint(model_dir_input)

        def session_init_op(_scaffold, sess):
            saver.restore(sess, checkpoint_path)
            tf.logging.info("Restored model from %s", checkpoint_path)

        scaffold = tf.train.Scaffold(init_fn=session_init_op)
        session_creator = tf.train.ChiefSessionCreator(scaffold=scaffold)
        with tf.train.MonitoredSession(
                session_creator=session_creator, hooks=hooks) as sess:
            sess.run([])
        # print(" ****** decoded string ", decoded_string)
        return decoded_string


@app.route("/examplesdata")
def examplesdata():
    source_data = data_utils.load_test_dataset()
    f_names = data_utils.generate_field_types(source_data)
    data_utils.forward_norm(source_data, destination_file, f_names)

    run_inference()

    # Perform post processing - backward normalization
    # decoded_post_array = []
    # for row in decoded_string:
    #     decoded_post = data_utils.backward_norm(row, f_names)
    #     decoded_post_array.append(decoded_post)

    decoded_string_post = data_utils.backward_norm(decoded_string[0], f_names)

    try:
        vega_spec = json.loads(decoded_string_post)
        vega_spec["data"] = {"values": source_data}
        response_payload = {"vegaspec": vega_spec, "status": True}
    except JSONDecodeError as e:
        response_payload = {
            "status": False,
            "reason": "Model did not produce a valid vegalite JSON",
            "vegaspec": decoded_string
        }
    return jsonify(response_payload)


@app.route("/")
def hello():
    return render_template('index.html')


"""[Load sample json data from new dataset]

Returns:
    [type] -- [description]
"""


@app.route("/testdata")
def testdata():
    return jsonify(data_utils.load_test_dataset())


@app.route("/testhundred", methods=['POST'])
def testhundred():
    input_data = request.json
    print("input data >>>>>>>>>", input_data)
    data = data_utils.get_test100_data(input_data["index"])
    response_payload = {"data": data, "status": True, "model": model_dir_input}
    return jsonify(response_payload)


@app.route("/savetest", methods=['POST'])
def savetest():
    input_data = request.json
    # print("input data >>>>>>>>>", input_data)
    data = data_utils.save_test_results(input_data)
    response_payload = {"status": True}
    return jsonify(response_payload)


@app.route("/inference", methods=['POST'])
def inference():
    input_data = request.json

    # Catch bad JSONDecodeError
    try:
        source_data = json.loads(str(input_data["sourcedata"]))
    except JSONDecodeError as e:
        response_payload = {
            "status": False,
            "reason": "Bad JSON: Unable to decode source JSON.  "
        }
        return jsonify(response_payload)

    if len(source_data) == 0:
        response_payload = {"status": False, "reason": "Empty JSON!!!!.  "}
        return jsonify(response_payload)

    # Perform preprocessing - forward normalization on first data sample
    f_names = data_utils.generate_field_types(source_data)
    fnorm_result = data_utils.forward_norm(source_data, destination_file,
                                           f_names)

    if (not fnorm_result):
        response_payload = {"status": False, "reason": "JSON decode error  "}
        return jsonify(response_payload)

    run_inference()

    # # Perform post processing - backward normalization
    # decoded_string_post = data_utils.backward_norm(decoded_string, f_names)
    # # print("**********",decoded_string_post)
    # try:
    #     vega_spec = json.loads(decoded_string_post)
    #     vega_spec["data"] = { "values": source_data}
    #     response_payload = {"vegaspec": vega_spec, "status": True}
    # except JSONDecodeError as e:
    #     response_payload = {"status": False,
    #     "reason": "Model did not produce a valid vegalite JSON.",
    #     "vegaspec": decoded_string}
    # return jsonify(response_payload)

    # Perform post processing - backward normalization
    decoded_post_array = []
    for row in decoded_string:
        decoded_post = data_utils.backward_norm(row, f_names)
        decoded_post_array.append(decoded_post)

    # decoded_string_post = data_utils.backward_norm(decoded_string, f_names)
    # print("==========", decoded_string)

    try:
        vega_spec = json.dumps(decoded_post_array)
        # print("===== vega spec =====", vega_spec)
        response_payload = {
            "vegaspec": vega_spec,
            "status": True,
            "data": source_data
        }
    except JSONDecodeError as e:
        response_payload = {
            "status": False,
            "reason": "Model did not produce a valid vegalite JSON",
            "vegaspec": decoded_string
        }
    return jsonify(response_payload)


if __name__ == "__main__":
    # tf.logging.set_verbosity(tf.logging.INFO)
    # tf.app.run()
    print("Starting webserver: ", ARGS)
    app.config['APPLICATION_ROOT'] = "static"
    app.run(host='0.0.0.0', debug=True, port=ARGS.port, threaded=True)
