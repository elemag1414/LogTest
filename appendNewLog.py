import os
import time
import random
import string
from github import Github
import datetime

# GitHub API를 사용하기 위한 토큰 설정
g = Github("your_github_token")

# 랜덤 문자열 생성 함수
def random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

# 랜덤 문자열을 history.log 파일에 추가하는 함수
def append_random_string_to_file(repo, path, message, branch):
    contents = repo.get_contents(path, ref=branch)
    now = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y")
    newMSG = random_string(10)
    print(f'Append New MSG {now}: {newMSG}')
    # repo.update_file(contents.path, message, contents.decoded_content.decode("utf8") + newMSG + '\n', contents.sha, branch=branch)
    repo.update_file(contents.path, message, contents.decoded_content.decode("utf8") + now + '\n', contents.sha, branch=branch)

# GitHub 레포지토리 설정
repo = g.get_user().get_repo("your_repo_name")

# 무한루프를 돌면서 일정 시간마다 랜덤 문자열을 history.log 파일에 추가
while True:
    append_random_string_to_file(repo, "history.log", "Add random string", "main")
    time.sleep(120)  # 120초마다 실행
