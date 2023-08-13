import os, json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


color_list = 'bgrcmyk'
len_color_list = len(color_list)

json_folder = './logs'
json_file = os.path.join(json_folder, 'hpo_expriments_summary_20230812_1837.json')

# print(os.path.exists(json_file))


def plot_data(data, idx, show_plot=True):
  summary = {'name': data['name']}
  train_loss = np.array(data['data']['train']['loss'])
  train_iou  = np.array(data['data']['train']['iou'])
  train_f1   = np.array(data['data']['train']['f1'])
  eval_loss  = np.array(data['data']['eval']['loss'])
  eval_iou   = np.array(data['data']['eval']['iou'])
  eval_f1    = np.array(data['data']['eval']['f1'])
  min_train_loss = train_loss.min()
  max_train_iou = train_iou.max()
  max_train_f1 = train_f1.max()
  min_eval_loss = eval_loss.min()
  max_eval_iou = eval_iou.max()
  max_eval_f1 = eval_f1.max()
  summary.update({'alpha': data['data']['alpha']})
  summary.update({'lambda_weight': data['data']['lambda_weight']})
  summary.update({'train': {'loss': min_train_loss, 'iou': max_train_iou, 'f1': max_train_f1}})
  summary.update({'eval': {'loss': min_eval_loss, 'iou': max_eval_iou, 'f1': max_eval_f1}})
  
  
  min_train_loss_epoch = np.argmin(train_loss) + 1
  max_train_iou_epoch = np.argmax(train_iou) + 1
  max_train_f1_epoch = np.argmax(train_f1) + 1
  min_eval_loss_epoch = np.argmin(eval_loss) + 1
  max_eval_iou_epoch = np.argmax(eval_iou) + 1
  max_eval_f1_epoch = np.argmax(eval_f1) + 1
  
  name = data['name']
  print(name)
  print(f"  [TRAIN] min_loss: {min_train_loss:.10f}, max_iou: {max_train_iou*100:.1f}%, max_f1: {train_f1.max()*100:.1f}%")
  print(f"  [EVAL]  min_loss: {min_eval_loss:.10f}, max_iou: {max_eval_iou*100:.1f}%, max_f1: {max_eval_f1*100:.1f}%")
  
  if show_plot: 
    # plot f1
    plt.subplot(1, 2, 1)

    plt.plot(list(range(1, len(train_f1)+1)), train_f1, f'{color_list[idx%len_color_list]}--', label=name)
    plt.plot([max_train_f1_epoch], [train_f1.max()], f'{color_list[idx%len_color_list]}o', markersize=10)
    plt.text(max_train_f1_epoch, train_f1.max(), f'{train_f1.max()*100:.1f}%@EP{max_train_f1_epoch}', verticalalignment='bottom')

    plt.plot(list(range(1, len(eval_f1)+1)), eval_f1, f'{color_list[idx%len_color_list]}-', label=name)
    plt.plot([max_eval_f1_epoch], [max_eval_f1], f'{color_list[idx%len_color_list]}o', markersize=10)
    plt.text(max_eval_f1_epoch, max_eval_f1, f'{max_eval_f1*100:.1f}%@EP{max_eval_f1_epoch}', verticalalignment='bottom')
    
    plt.ylabel('F1')
    plt.ylim([0, 1])
    plt.xlim([0, 500])
    plt.yticks(np.arange(0, 1.0, .1))
    plt.legend()
    plt.grid(True)
    plt.xlabel('Epoch')
    plt.xticks(np.arange(0, 500, 50))
    
    # plot loss
    plt.subplot(1, 2, 2)

    plt.plot(list(range(1, len(train_loss)+1)), train_loss, f'{color_list[idx%len_color_list]}--', label=name)
    plt.plot([min_train_loss_epoch], [min_train_loss], f'{color_list[idx%len_color_list]}o', markersize=10)
    plt.text(min_train_loss_epoch, min_train_loss, f'{min_train_loss:.4f}@EP{min_train_loss_epoch}', verticalalignment='bottom')

    plt.plot(list(range(1, len(eval_loss)+1)), eval_loss, f'{color_list[idx%len_color_list]}-', label=name)
    plt.plot([min_eval_loss_epoch], [min_eval_loss], f'{color_list[idx%len_color_list]}o', markersize=10)
    plt.text(min_eval_loss_epoch, min_eval_loss, f'{min_eval_loss:.4f}@EP{min_eval_loss_epoch}', verticalalignment='bottom')

    plt.ylabel('Loss')
    # plt.ylim([0, 1000])
    plt.xlim([0, 500])
    plt.yticks(np.arange(0, 1.0, .1))
    plt.legend()
    plt.grid(True)
    plt.xlabel('Epoch')
    plt.xticks(np.arange(0, 500, 50))
  
  return summary
  

with open(json_file, 'r') as f:
  _data = json.load(f) 
    
data = []
for blob in _data:
  name = f"alpha_{blob['alpha']}_lambda_{blob['lambda_weight']}"
  data.append({'name': name, 'data': blob})


plot_result = False
if plot_result: plt.figure(figsize=(16,10))
summary = []
for idx, blob in enumerate(data, start=0):
  _summary = plot_data(blob, idx, show_plot=plot_result)
  summary.append(_summary)
  print(json.dumps(_summary, indent=2))
  

if plot_result:
  plt.tight_layout()
  plt.show()




results = {'lambda_weights': [], 'train': {'loss': [], 'iou': [], 'f1': []}, 'eval': {'loss': [], 'iou': [], 'f1': []}}
lambda_weights = []
train_f1 = []
eval_f1 = []

for blob in summary:
  if blob['alpha'] == 0.25:
    lambda_weights.append(blob['lambda_weight'])
    train_f1.append(blob['train']['f1'])
    eval_f1.append(blob['eval']['f1'])
    results['lambda_weights'].append(blob['lambda_weight'])
    results['train']['loss'].append(blob['train']['loss'])
    results['train']['iou'].append(blob['train']['iou'])
    results['train']['f1'].append(blob['train']['f1'])
    results['eval']['loss'].append(blob['eval']['loss'])
    results['eval']['iou'].append(blob['eval']['iou'])
    results['eval']['f1'].append(blob['eval']['f1'])

    # print(f"{blob['name']}: {blob['lambda_weight'], blob['train']['f1']}")

# plt.plot(lambda_weights, train_f1)
# plt.grid(True)
# plt.show()

data = {
          "lambda_weights": results['lambda_weights'], 
          "train_f1": results['train']['f1'], 
          "eval_f1": results['eval']['f1'], 
          "train_iou": results['train']['iou'], 
          "eval_iou": results['eval']['iou'], 
        }
df = pd.DataFrame(data)

# ANSI escape 코드
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
ENDC = '\033[0m'
  
print(f"\n\nHPO Summary at alpha: 0.25")

# 최대값을 사이언색으로 표시하고, 동일한 너비로 포매팅하는 함수
def color_and_format(val, max_val, width):
    formatted_val = f"{val:.6f}".center(width)
    if val == max_val:
        return BOLD + CYAN + formatted_val + ENDC
    return formatted_val

# 각 열의 최대 너비 계산 (헤더와 각 행의 셀 길이 중에서 가장 큰 값)
max_widths = [max([len(f"{x:.6f}") for x in df[col]] + [len(col)]) for col in df.columns]

# 각 열의 최대값에 색상 적용 및 포매팅
for col in df.columns:
    max_val = df[col].max()
    df[col] = df[col].apply(lambda x: color_and_format(x, max_val, max_widths[df.columns.get_loc(col)]))

# DataFrame을 문자열로 변환하고 각 셀을 가운데로 정렬
header = [col.center(width) for col, width in zip(df.columns, max_widths)]
print(' | '.join(header))
print('-' * sum(max_widths) + '-' * (3 * (len(df.columns) - 1)))
for _, row in df.iterrows():
    print(' | '.join(row))