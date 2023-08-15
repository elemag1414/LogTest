import os, json
import numpy as np
import matplotlib.pyplot as plt
from termcolor import colored

def custom_decoder(dct):
  return {k: float('nan') if v == "NaN" else v for k, v in dct.items()}


def print_best_trial(data, best_id):
  best_metric = data[best_id]
  print(colored("\nBest Trial:", "yellow"))
  print(f"  - trial_id: {best_metric['trial_id']}")
  print(f'  - eval f1: {best_metric["best_eval_f1"]*100:.2f}%')
  print(f'  - eval epoch: {best_eval_epoch+1}')
  print(f'  - train f1: {best_metric["best_train_f1"]*100:.2f}%')
  print(f'  - alpha: {best_metric["alpha"]}')
  print(f'  - gamma: {best_metric["gamma"]}')
  print(f'  - weight_dice: {best_metric["weight_dice"]}')
  print(f'  - weight_focal: {best_metric["weight_focal"]}')

data_file = './logs/Optuna_DLV3+_ResNet50_20230814_2104.json'

with open(data_file, 'r') as f:
  data = json.load(f, object_hook=custom_decoder)


best_id = -1
best_eval_f1_values = []
best_eval_f1 = -1
proc_time = []
_eval_f1_lists = []
for idx, blob in enumerate(data, start=0):
  eval_f1 = blob['best_eval_f1']
  if np.isnan(eval_f1):
    # print(colored(f"NaN at trial {idx+1}", "red"))
    _eval_f1_lists.append(-1)
  else: 
    _eval_f1_lists.append(eval_f1)
  if eval_f1 > best_eval_f1:
    best_eval_f1 = eval_f1
    best_id = idx
  best_eval_f1_values.append(eval_f1)
  proc_time.append(blob['proc_time'])
  # print(f"[{blob['trial_id']}] eval_f1: {eval_f1}, train_f1: {blob['best_train_f1']}, dice: {blob['weight_dice']:.3f}, focal: {blob['weight_focal']:.3f}, alpha: {blob['alpha']}, gamma: {blob['gamma']}")


# Sort data according to best_eval_f1
# print(f"\n_eval_f1_lists: {_eval_f1_lists}")
sorted_indices = list(np.argsort(_eval_f1_lists)[::-1])
# print(f"sorted_indices: {sorted_indices}")
sorted_data = [data[i] for i in sorted_indices]

print(colored("\n*** Sorted Results ***", "green"))
for idx, blob in enumerate(sorted_data, start=0):
  print(f"[{idx+1:02d}] eval_f1: {blob['best_eval_f1']:6.4f} (id: {blob['trial_id']:02d}), train_f1: {blob['best_train_f1']:6.4f}, dice: {blob['weight_dice']:.3f}, focal: {blob['weight_focal']:.3f}, alpha: {blob['alpha']:.4f}, gamma: {blob['gamma']:.4f}")
print(" ")

current_num_trials = len(data)
total_num_trials = data[0]['num_trial']
mean_proctime = np.array(proc_time).mean()
ETA = (total_num_trials - current_num_trials) * mean_proctime
hour = int(ETA//3600)
_min = int((ETA - hour*3600)//60)
sec = int(ETA - hour*3600 - _min * 60)
print(colored(f"ETA: {hour}h {_min}m {sec}s", "cyan"))

best_metric = data[best_id]
best_eval_epoch = np.argmax(best_metric['eval_f1'])
epochs = list(range(1, len(best_metric['eval_f1'])+1))

print_best_trial(data, best_id)

# print(json.dumps(best_metric, indent=2))
plt.figure(figsize=(10,8))
plt.plot(epochs, best_metric['train_f1'], 'b--', label='train')
plt.plot(epochs, best_metric['eval_f1'], 'b-', label='eval')

plt.plot(best_eval_epoch+1, best_metric['eval_f1'][best_eval_epoch], 'ro')
plt.text(best_eval_epoch+1, best_metric['eval_f1'][best_eval_epoch], f'{best_metric["best_eval_f1"]*100:.1f}%@EP{best_eval_epoch+1}', verticalalignment='bottom')

plt.grid(True)
plt.legend()
plt.xlabel('epoch')
plt.ylabel('f1')
plt.ylim([0, 1])
plt.title(f"Best Trial-{data[best_id]['trial_id']}")
plt.show()