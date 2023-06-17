import os, re, json
from termcolor import colored 
from GitHubUtils import (
  set_github_obj,
  get_github_ll,
  get_github_file
)
import subprocess

def create_dir(_path):
  if not os.path.exists(_path):
    os.makedirs(_path)

def color_msg(msg, color='white'):
  return colored(msg, color=color)

def convert_log(file_name):
  assert os.path.exists(file_name), colored(f"[convert_log] file not found: {file_name}", "red")
  with open(file_name, 'r') as f:
    lines = f.readlines()

  parsed_data = []
  lines_iter = iter(lines)

  header_found = False
  header = []
  body = []
  epoch_lists = []

  for line in lines_iter:

    if line.startswith('**'):
      header_found = True
    
    if header_found:
      header.append(line)
      if line.startswith('}'):
        header_found = False
      continue

    # parsed_data를 찾습니다.
    if line.startswith('@') or line.startswith('['):
      if '--- Finished' in line:
        continue
      body.append(line)
      epoch_data = {}
      
      key, value = line[1:].split(' ', 1)  # 첫 번째 공백에서 분리합니다.
      
      # epoch 값을 파싱합니다.
      epoch = int(re.search(r'\d+', value).group())
      epoch_lists.append(epoch)
      epoch_data['epoch'] = epoch
      
      # train과 eval 세션을 파싱합니다.
      for session in ['ep', 'train', 'eval']:
        session_start = value.find(f'[{session.upper()}]') + len(session) + 3

        # "[EVAL]" 다음에 오는 "[...]" 문자열을 건너뛰기 위해 정규식을 사용합니다.
        if session == 'eval':
          next_bracket = re.search(r'\[.*?\]', value[session_start:])
          if next_bracket:
            session_start += next_bracket.end()
        
        # to parse lr
        if session == 'ep':
          session_start += value[session_start:].find(']') + len(']')

        session_end = value.find('[', session_start+1)

        if session_end == -1:
            session_end = None
        
        session_str = value[session_start:session_end]
        session_items = session_str.split(', ')
        session_data = {}
        for item in session_items:
          try:
            k, v = item.split(': ')
            # "%"가 포함된 항목은 퍼센트를 제거하고 float으로 변환합니다.
            if '%' in v:
              v_index = v.find('%')
              v = v[:v_index]
              # print(f"removed % : {v}")
            # "ms" 또는 "m"가 포함된 항목은 무시합니다.
            elif 'ms' in v or 'm' in v:
              continue
            # iou 값은 공백을 제거하고 float으로 변환합니다.
            elif 'iou' in k:
              # print(f"iou: {k}")
              v = v.split(' ')[0]
            session_data[k.strip()] = float(v)
          except ValueError:
            # print('Value ERROR')
            pass
        
        epoch_data[session] = session_data
      
      parsed_data.append(epoch_data)

  lr = []
  train_accu = []
  train_iou = []

  train_f1 = []
  train_loss = []
  eval_accu = []
  eval_iou = []
  eval_f1 = [] 
  eval_loss = []
  for blob in parsed_data:
    train_accu.append(blob['train']['accu-50'])
    train_iou.append(blob['train']['iou'])
    if 'f1' in list(blob['train'].keys()):
      train_f1.append(blob['train']['f1'])
      eval_f1.append(blob['eval']['f1'])
    train_loss.append(blob['train']['loss'])

    eval_accu.append(blob['eval']['accu-50'])
    eval_iou.append(blob['eval']['iou'])
    eval_loss.append(blob['eval']['loss'])
    if 'lr' in list(blob['ep'].keys()):
      lr.append(blob['ep']["lr"])

  return header, body, epoch_lists, {'lr': lr, 'train': {'accu': train_accu, 'iou': train_iou, 'f1': train_f1, 'loss': train_loss}, 'eval': {'accu': eval_accu, 'iou': eval_iou, 'f1': eval_f1, 'loss': eval_loss}}


def parseEpoch(lines, search_epoch):
  line_number = 0
  epoch = []
  for idx, line in enumerate(lines):
    tmp = line.split('[')[1].strip()
    start_index = tmp.find('EP ') + len('EP ')
    end_index = tmp.find('/')
    _epoch = int(tmp[start_index:end_index])
    epoch.append(_epoch)
    if _epoch == search_epoch:
      line_number = idx
  return line_number, epoch

def merge_log_files(log_file1, log_file2):
  assert os.path.exists(log_file1), colored(f"[merge_log_files] log file not found: {log_file1}", "red")
  assert os.path.exists(log_file2), colored(f"[merge_log_files] log file not found: {log_file2}", "red")
  header1, body1, epoch_lists1, data1 = convert_log(log_file1)
  header2, body2, epoch_lists2, data2 = convert_log(log_file2)

  ### Replace Name of header with new merged one
  header1_name, _ = json_header(header1)
  header2_name, _ = json_header(header2)
  newName = header1_name + '_' + header2_name
  header2[0] = header2[0].replace(header2_name, newName)

  _, epoch2 = parseEpoch(body2, 0)
  assert len(epoch2) > 0, colored(f"{log_file2} doesn't have epoch info", "red")

  line_number, _ = parseEpoch(body1, epoch2[0])
  assert line_number > 1, colored(f"{log_file1} doesn't have epoch {epoch2[0]}", "red")

  mergeLog = header2 + ['\n'] + body1[:line_number] + body2

  file_cwd = os.path.dirname(os.path.abspath(__file__))
  merge_file = f'logs/train_log_main_merge_{header1_name}_{header2_name}.txt'
  with open(os.path.join(file_cwd, merge_file), 'w') as f:
    [f.write(x) for x in mergeLog]

def json_header(header):
  body = ''
  for line in header:
    line = line.strip()
    if line.startswith('**'):
      idx = line.find("on ") + len("on ")
      name = line[idx:]
    else:
      body += line
  
  if len(name.split('_')) > 2:
    name = '_'.join(name.split('_')[-2:]) + 'm'
  json_body = json.loads(body)
  return name, json_body


def convertToJSONTask():
  file_cwd = os.path.dirname(os.path.abspath(__file__))
  local_log_path = os.path.join(file_cwd, 'logs')
  local_log_files = [os.path.join(local_log_path, x) for x in os.listdir(local_log_path) if x.startswith('train_log') or x.startswith('merge_')]

  etri_data = []
  electron_data = []
  disp = True
  possible_merge_files = []
  for idx, _file in enumerate(local_log_files, start=1):
    header, body, epoch_lists, data = convert_log(_file)
    name, header_json = json_header(header)
    HOST = header_json['HOST'] 
    print(color_msg(f"{os.path.basename(_file):<35}\t", "yellow"), color_msg(f"HOST: {HOST}", "green"))
      
    print(f"num_epochs: {header_json['num_epochs']}")
    print(f"NumEpochs: {len(epoch_lists)}")
    print(f"is resume? {header_json['resume']}")  #resumeWeight
    if header_json['resume']:
      resumeWeight = header_json['resumeWeight']
      print(color_msg(f"  {resumeWeight}", "cyan"))

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
  with open(os.path.join(local_log_path, 'etri_data_json.json'), 'w') as f:
      json.dump(etri_data, f)
  with open(os.path.join(local_log_path, 'electron_data_json.json'), 'w') as f:
      json.dump(electron_data, f)

  print(colored(f"\n\nconvertToJSONTask done"))


def gitHubTask():
  set_github_obj()
  file_lists = get_github_ll('logs')
  print(f"[gitHubTask] file_lists: {file_lists}")
  for _file in file_lists:
    print(colored(f"Fetch {_file}", "yellow"))
    file_cwd = os.path.dirname(os.path.abspath(__file__))
    contents = get_github_file(_file)
    with open(os.path.join(file_cwd, _file), 'w') as f:
      f.write(contents)
