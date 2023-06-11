import os, json, time
from github import Github
from github import GithubException
from termcolor import colored 
from GitHubUtils import (
  set_github_obj,
  github_ll,
  github_file_content
)
from Utils import (
  create_dir,
  convert_log_whole,
  merge_log_files
)

def color_msg(msg, color='white'):
  return colored(msg, color=color)

def json_header(header):
  body = ''
  for line in header:
    line = line.strip()
    if line.startswith('**'):
      idx = line.find("on ") + len("on ")
      name = line[idx:]
    else:
      body += line
  json_body = json.loads(body)
  return name, json_body


def convertToJSONTask():
  local_log_path = 'logs'
  local_log_files = [os.path.join(local_log_path, x) for x in os.listdir(local_log_path) if x.startswith('train_log') and not '_merge_' in x]

  etri_data = []
  electron_data = []
  disp = True
  for idx, _file in enumerate(local_log_files, start=1):
    header, body, epoch_lists, data = convert_log_whole(_file)
    name, header_json = json_header(header)
    HOST = header_json['HOST'] 
    print(color_msg(f"{os.path.basename(_file):<35}\t", "yellow"), color_msg(f"HOST: {HOST}", "green"))
    if disp:
      disp = False
      print(json.dumps(header_json, indent=2))
      
    print(f"num_epochs: {header_json['num_epochs']}")
    print(f"NumEpochs: {len(epoch_lists)}")
    print(f"is resume? {header_json['resume']}")  #resumeWeight
    if header_json['resume']: print(color_msg(f"  {header_json['resumeWeight']}", "cyan"))

    if HOST.lower() == 'etri':
      print(colored(f" {idx} etri", "red"))
      etri_data.append({name: {'config': header_json, 'data': data}})
    elif HOST.lower() == 'electron' or HOST.lower() == 'elctron':
      print(colored(f" {idx} electron", "red"))
      electron_data.append({name: {'config': header_json, 'data': data}})
  
  print(f"Num etri_data: {len(etri_data)} ") 
  [print("  ", list(x.keys())[0]) for x in etri_data]
  print(f"Num electron_data: {len(electron_data)} ")
  [print("  ", list(x.keys())[0]) for x in electron_data]

  # write to JSON file
  with open('logs/etri_data_json.json', 'w') as f:
      json.dump(etri_data, f)
  with open('logs/electron_data_json.json', 'w') as f:
      json.dump(electron_data, f)

def gitHubTask():
  set_github_obj()
  file_lists = github_ll('logs')
  print(file_lists)
  for _file in file_lists:
    print(colored(f"Fetch {_file}", "yellow"))
    contents = github_file_content(_file)
    with open(_file, 'w') as f:
      f.write(contents)


if __name__ == '__main__':
  print(colored("Fetching Logs in GitHub and Save them locally...", "yellow"))
  gitHubTask()
  print(colored("Parse and Convert locally saved logs to JSON...", "yellow"))
  convertToJSONTask()
