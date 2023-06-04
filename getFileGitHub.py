import os
import time
import random
import string
from github import Github
import datetime

last_eval_accu = 0
# GitHub API를 사용하기 위한 토큰 설정
g = Github("your_token")

# Then play with your Github objects:
repo = g.get_repo("your_repo")

# Get ETRI Log
file_name = 'train_log_main.log'
file_content = repo.get_contents(file_name, ref="main")
file_data = file_content.decoded_content.decode()  # this is a string of the file data
with open(file_name, "w") as file:
    file.write(file_data)
print(f'Received {file_name} successfully')
    
# Get ELECTRON Log
file_name = 'train_log_electron.log'
file_content = repo.get_contents(file_name, ref="main")
file_data = file_content.decoded_content.decode()  # this is a string of the file data
with open(file_name, "w") as file:
    file.write(file_data)
print(f'Received {file_name} successfully')


print('DONE')
