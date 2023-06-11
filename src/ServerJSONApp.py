import os, json
from flask import Flask, jsonify
from Utils import convert_log_new
from termcolor import colored 
from newGitFetch import (
  gitHubTask,
  convertToJSONTask
)
app = Flask(__name__)


@app.route('/data_lists', methods=['GET'])
def data_lists():
  data_list = {}
  names = []
  for data in etri_data:
    name = list(data.keys())[0]
    names.append(name)
  data_list.update({"etri_data": names})
  names = []
  for data in electron_data:
    name = list(data.keys())[0]
    names.append(name)
  data_list.update({"electron_data": names})

  return jsonify(data_list)

@app.route('/data/<node_name>/<data_name>')
def get_plot_data(node_name, data_name):
  print(colored(f"node_name: {node_name}, data_name: {data_name}", "yellow"))

  return_obj = None
  if node_name == 'etri_data':
    for blob in etri_data:
      _key = list(blob.keys())[0]
      if _key == data_name:
        return_obj = blob[_key]
  elif node_name == 'electron_data':
    for blob in electron_data:
      _key = list(blob.keys())[0]
      if _key == data_name:
        return_obj = blob[_key]
  return jsonify({'data': return_obj})

@app.route('/data/new_fetch', methods=['GET'])
def update_whole_logs():
  global electron_data, etri_data
  print(colored("Fetch GitHub Log Files", "green"))
  gitHubTask()
  print(colored("Convert Log files to JSON Objects", "green"))
  convertToJSONTask()

  with open('logs/electron_data_json.json', 'r') as f:
    electron_data = json.load(f)
  
  with open('logs/etri_data_json.json', 'r') as f:
    etri_data = json.load(f)

  return jsonify({"result": "OK"})

# @app.route('/data/<req_data>', methods=['GET'])
# def get_home_data(req_data):
#   if req_data == 'home_data':
#     print('fetch request home_data received')
#     return jsonify(home_data)
#   elif req_data == 'electron_data':
#     print('fetch request for electron_data received')
#     return jsonify(electron_data)
#   else:
#     print('Unknown Request data type')
#     return ""

# @app.route('/reload/<req_data>', methods=['GET'])
# def reload_data(req_data):
#   global home_data, electron_data
#   if req_data == 'home_data':
#     print('Reload home_data...')
#     home_data = convert_log_new(home_log_file)
#     return jsonify(home_data)
#   elif req_data == 'electron_data':
#     print('Reload home_data...')
#     electron_data = convert_log_new(electron_log_file)
#     return jsonify(electron_data)
#   else:
#     print('Unknown Request data type')
#     return ""

if __name__ == '__main__':

  # print(colored("Fetch GitHub Log Files", "green"))
  # gitHubTask()
  # print(colored("Convert Log files to JSON Objects", "green"))
  # convertToJSONTask()


  with open('logs/electron_data_json.json', 'r') as f:
    electron_data = json.load(f)
  
  with open('logs/etri_data_json.json', 'r') as f:
    etri_data = json.load(f)

  # print(f"etri_data: {etri_data}")
  app.run(host='0.0.0.0', port=5000, debug=True)