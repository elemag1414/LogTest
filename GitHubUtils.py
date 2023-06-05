import os
import time
import random
import string
from github import Github
from github import GithubException
import datetime
from termcolor import colored
from  dotenv import dotenv_values

# GitHub API를 사용하기 위한 토큰
env_path = os.path.join('/'.join(os.path.abspath(__file__).split('/')[:-1]), ".env")
print(f'ENV PATH: {env_path}, found: {os.path.exists(env_path)}')
gitConfig = dotenv_values(env_path) 
g = Github(gitConfig['GITHUB_TOKEN'])
repo_name = gitConfig['GITHUB_REPO']

# log_file = 'train_log_main.log'
# repo = g.get_user().get_repo(repo_name)

repo = None

### helper functions
def color_str(msg, color='white'):
  return colored(msg, color)

def time_stamp():
  now = time.localtime()
  TIMESTR = time.strftime('%Y%m%d_%H%M', now)
  return TIMESTR

def set_github_obj():
  global repo
  # Then play with your Github objects:
  try: 
    repo = g.get_user().get_repo(repo_name)
    return True
  except GithubException as e:
    print(colored(f"[Github] set_github_obj Says: {e.data['message']} (error code: {e.status})", "yellow"))
    return False

def github_create_file(file_name, file_contents):
  if not repo:
    return False
  
  try:
    commit_msg = "Create File Test"
    repo.create_file(file_name, commit_msg, file_contents, branch="main")
    print(colored(f"[Github] file created: {file_name}", "green"))
    return True
  except GithubException as e:
    print(colored(f"[Github] github_create_file Says: {e.data['message']} (error code: {e.status})", "yellow"))
    return False

def github_delete_file(file_name):
  if not repo:
    return False
  
  try:
    file_to_delete = repo.get_contents(file_name, ref="main")
    repo.delete_file(file_to_delete.path, "Delete test.txt", file_to_delete.sha, branch="main")
    print(colored(f"[Github] file deleted: {file_name}", "yellow"))
    return True
  except GithubException as e:
    print(colored(f"[Github] github_delete_file Says: {e.data['message']} (error code: {e.status})", "yellow"))
    return False 
  
def github_ll(dir=""):
  if not repo:
    return False
  
  try: 
    contents = repo.get_contents(dir, ref="main")
    print(colored(f"[Github] github_ll:", "green"))
    for content_file in contents:
      print("  ", content_file.path)
    return True
  
  except GithubException as e:
    print(colored(f"[Github] github_ll Says: {e.data['message']} (error code: {e.status})", "yellow"))
    return False

def github_cat(file_name):
  if not repo:
    return False
  
  try:
    file_content = repo.get_contents(file_name, ref="main")
    file_data = file_content.decoded_content.decode()
    print(colored(f"[Github] github_ll:", "green"))
    for cnt, line in enumerate(file_data.split('\n'), start=1):
      line_num = color_str(f" {cnt:04d}", "white")
      print(f"{line_num}: {line}")
    return True

  except GithubException as e:
    print(colored(f"[Github] github_cat Says: {e.data['message']} (error code: {e.status})", "yellow"))
    return False
  

def github_logging(log_file, message, tm=True):
  branch = "main"
  commit_message = "Add new message"
  contents = repo.get_contents(log_file, ref=branch)

  if tm:
    message = f'@{time_stamp()} '+ message
    
  while True:
    try: 
      repo.update_file(contents.path, commit_message, contents.decoded_content.decode("utf8") + message + '\n', contents.sha, branch=branch)
      print(colored('[Github] Git Log Updated...', "green"))
      break
    except: 
      now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      print(colored(f'[Github[ @{now} Fail to update log! ({now}). Try again in 10s', "green"))
    time.sleep(10)

######
### For appTest
def append_string_to_file(repo, path, message, commit_message, branch):
  contents = repo.get_contents(path, ref=branch)

  while True:
    try: 
      repo.update_file(contents.path, commit_message, contents.decoded_content.decode("utf8") + message + '\n', contents.sha, branch=branch)
      break
    except: 
      now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      print(f'[{now}] Fail to update log! ({now}). Try again in 10s')
    time.sleep(10)

def appTest(log_file):

  assert repo, colored("[Github] repo object not inited!", "red")

  epoch = 1
  last_eval_accu = 0

  now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
  message = f'\n\n** NEW EXPERIMENT on {now}'
  print(message)
  append_string_to_file(repo, log_file, message, "Add new message", "main")

  # 무한루프를 돌면서 일정 시간마다 history.log 파일에 추가
  while True:
      accuracy = random.randint(-20, 100)

      now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      _accuracy = last_eval_accu + accuracy
      last_eval_accu = _accuracy
      newMSG = f'** @{now}: \n\t[Epoch {epoch:03d}] eval_accu: {_accuracy/10:.1f}%'
      print(newMSG)
      append_string_to_file(repo, log_file, newMSG, "Add new message", "main")
   
      time.sleep(120)  # 120초마다 실행
      epoch += 1

if __name__ == '__main__':
  # GitHub 레포지토리 설정
  set_github_obj()
  log_file = 'train_log_main_test.log'
  github_create_file(log_file, file_contents='')
  appTest(log_file)