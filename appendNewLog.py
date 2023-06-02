import os
import time
import random
import string
from github import Github
import datetime

# GitHub API를 사용하기 위한 토큰 설정
g = Github("your_github_token")

# 랜덤 문자열 생성 함수 (optional)
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# history.log 파일에 메시지 추가하는 함수
def append_random_string_to_file(repo, path, message, epoch, accuracy, branch):
    contents = repo.get_contents(path, ref=branch)
    now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    newMSG = f'** @{now}: \n\t[Epoch {epoch:03d}] eval_accu: {accuracy/10:.1f}%'
    print(newMSG)
    repo.update_file(contents.path, message, contents.decoded_content.decode("utf8") + newMSG + '\n', contents.sha, branch=branch)

# GitHub 레포지토리 설정
repo = g.get_user().get_repo("your_repo_name")
epoch = 1

# 무한루프를 돌면서 일정 시간마다 메시지를 history.log 파일에 추가
while True:

    accuracy = random.randint(550, 1000)
    try:
      append_random_string_to_file(repo, "history.log", "Add new message", epoch, accuracy, "main")
    except:
      now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
      print(f'Fail to update log! ({now})')
    time.sleep(120)  # 120초마다 실행
    epoch += 1
