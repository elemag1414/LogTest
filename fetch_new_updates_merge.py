import os, json, time
from  dotenv import dotenv_values
from github import Github
from github import GithubException
from termcolor import colored 
from GitHubUtils import (
  set_github_obj,
  get_github_ll,
  get_github_file
)
from Utils import (
  create_dir,
  convert_log,
  merge_log_files
)


# GitHub API를 사용하기 위한 토큰
env_path = os.path.join('/'.join(os.path.abspath(__file__).split('/')[:-1]), "..", ".env")
gitConfig = dotenv_values(env_path) 
g = Github(gitConfig['GITHUB_TOKEN'])
repo_name = gitConfig['GITHUB_REPO']

gFolder = 'logs'
active_log_file = None

def fetch_new_logs():
  global active_log_file
  ll_lists = get_github_ll(gFolder)
  print(colored(f"File Lists on {gFolder}", "yellow"))
  [print(f"  [{cnt}] {x}") for cnt, x in enumerate(ll_lists, start=1)]

  print(' ')
  while True:
    uIn = input(f"Select Log File [{1} - {len(ll_lists)}]: ")
    uIn = uIn.strip()
    try:
      uIn = int(uIn)
    except:
      print("  Incorect input. Enter integer number\n")
      continue

    if uIn < 1 or uIn > len(ll_lists):
      print(f"  Enter in range between 1 - {len(ll_lists)}")
      continue
    else:
      active_log_file = ll_lists[uIn-1]
      break

  print('Log File: ', active_log_file)

  ### Get active_log_file contents
  file_contents = get_github_file(active_log_file)

  ### Save file locally
  local_folder = os.path.dirname(active_log_file)
  print(f"Local Folder: {local_folder}")
  create_dir(local_folder)
  with open(active_log_file, 'w') as f:
    f.write(file_contents)
  
  print(colored(f'{repo_name}/{active_log_file} saved on locally', 'yellow'))
 


  
if __name__ == '__main__':

  # Fetch Updates on Github
  assert set_github_obj(), colored("ERROR: Failed to Initialize GitHub Access Obj", "red")
  print(colored("Fetch Updates...", "green"))
  fetch_new_logs()  
  time.sleep(1)

  # Merge Two locally saved Log Files
  print(colored("Merge Two Fetch Files...", "green"))
  log_file1 = 'logs/train_log_main_20230605_1912.txt'
  log_file2 = 'logs/train_log_main_20230607_1302.txt'
  merge_log_files(log_file1, log_file2)
  time.sleep(1)

  header, body, data = convert_log('logs/merge_train_log_main_20230605_1912_20230605_1912.txt')
  # print(json.dumps(data, indent=2))
  num_epoch = len(data['train']['f1'])

  print(f"Total Epochs: {num_epoch}")


