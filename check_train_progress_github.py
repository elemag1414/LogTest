import os, json, re, time
import matplotlib.pyplot as plt
import numpy as np
import subprocess
from termcolor import colored 
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import argparse

# Initialize parser
parser = argparse.ArgumentParser()

# Adding optional argument
parser.add_argument("--fetch", action='store_true', help="Set fetch flag")

# Parse the arguments
args = parser.parse_args()

github_fetch = args.fetch
canvas = None
fig = None
ax = None
current_graph_number = 1
current_menu = 'iou'
prev_epoch_file = 'lastEpoch.txt'
fetch_file = "getFileGitHub.py"

def cprint(msg, color='white'):
  print(colored(msg, color=color))  

def exponential_moving_average(data, alpha):
  """
  Compute the exponential moving average of data.

  Parameters:
  - data: A list of float values.
  - alpha: The smoothing factor, between 0 and 1. Smaller values result in more smoothing.

  Returns:
  - A list of float values representing the exponential moving average of data.
  """
  ema_data = []
  ema = data[0]
  for d in data:
    ema = alpha * d + (1 - alpha) * ema
    # ema = (1 - alpha) * d + alpha * ema
    ema_data.append(ema)
  return ema_data

def convert_log(file_name):
  with open(file_name, 'r') as f:
    # lines = f.read()
    lines = f.readlines()

  parsed_data = []
  lines_iter = iter(lines)

  for line in lines_iter:
    # parsed_data를 찾습니다.
    if line.startswith('@') or line.startswith('['):
      epoch_data = {}
      
      key, value = line[1:].split(' ', 1)  # 첫 번째 공백에서 분리합니다.
      
      # epoch 값을 파싱합니다.
      epoch = int(re.search(r'\d+', value).group())
      epoch_data['epoch'] = epoch
      
      # train과 eval 세션을 파싱합니다.
      for session in ['train', 'eval']:
        session_start = value.find(f'[{session.upper()}]') + len(session) + 3

        # "[EVAL]" 다음에 오는 "[...]" 문자열을 건너뛰기 위해 정규식을 사용합니다.
        if session == 'eval':
          next_bracket = re.search(r'\[.*?\]', value[session_start:])
          if next_bracket:
            session_start += next_bracket.end()
        
        session_end = value.find('[', session_start+1)

        if session_end == -1:
            session_end = None
        
        # print(f'{session} session start: {session_start}, end: {session_end}')

        session_str = value[session_start:session_end]
        session_items = session_str.split(', ')
        session_data = {}
        # print(session_items)
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

  train_accu = []
  train_iou = []
  train_loss = []
  eval_accu = []
  eval_iou = []
  eval_loss = []
  for blob in parsed_data:
    train_accu.append(blob['train']['accu-50'])
    train_iou.append(blob['train']['iou'])
    train_loss.append(blob['train']['loss'])
    eval_accu.append(blob['eval']['accu-50'])
    eval_iou.append(blob['eval']['iou'])
    eval_loss.append(blob['eval']['loss'])

  return {'train': {'accu': train_accu, 'iou': train_iou, 'loss': train_loss}, 'eval': {'accu': eval_accu, 'iou': eval_iou, 'loss': eval_loss}}

def draw_graph(slider_value):
  global canvas, current_graph_number, fig, ax, current_menu
  alpha = 1-float(slider_value)

  if canvas:
    canvas.get_tk_widget().grid_forget()

  if fig is not None: # check if fig exists
      fig.clear() # clear existing plot
  
  fig = Figure(figsize=(7, 6), dpi=100)
  ax = fig.add_subplot(111)
  t = np.arange(0, 3, .01)

  # Depending on the selection plot the corresponding graph
  if current_graph_number == 1:
    HOST = 'ETRI IOU'
    if current_menu == 'iou':
      train_data = np.array(exponential_moving_average(etri_data['train']['iou'], alpha))
      eval_data = np.array(exponential_moving_average(etri_data['eval']['iou'], alpha))
    elif current_menu == 'loss':
      train_data = np.array(exponential_moving_average(etri_data['train']['loss'], alpha))
      eval_data = np.array(exponential_moving_average(etri_data['eval']['loss'], alpha))
    elif current_menu == 'accu':
      train_data = np.array(exponential_moving_average(etri_data['train']['accu'], alpha))
      eval_data = np.array(exponential_moving_average(etri_data['eval']['accu'], alpha))

    numEpoch = len(train_data)
    
    ax.plot(np.array(range(1, numEpoch+1)), train_data, color='blue', label=f'train_{current_menu}')
    ax.plot(np.array(range(1, numEpoch+1)), eval_data, color='red', label=f'eval_{current_menu}')
    
  elif current_graph_number == 2:
    HOST = 'ELECTRON IOU'
    if current_menu == 'iou':
      train_data = np.array(exponential_moving_average(electron_data['train']['iou'], alpha))
      eval_data = np.array(exponential_moving_average(electron_data['eval']['iou'], alpha))
    elif current_menu == 'loss':
      train_data = np.array(exponential_moving_average(electron_data['train']['loss'], alpha))
      eval_data = np.array(exponential_moving_average(electron_data['eval']['loss'], alpha))
    elif current_menu == 'accu':
      train_data = np.array(exponential_moving_average(electron_data['train']['accu'], alpha))
      eval_data = np.array(exponential_moving_average(electron_data['eval']['accu'], alpha))

    numEpoch = len(train_data)
    
    ax.plot(np.array(range(1, numEpoch+1)), train_data, color='blue', label=f'train_{current_menu}')
    ax.plot(np.array(range(1, numEpoch+1)), eval_data, color='red', label=f'eval_{current_menu}')
  
  # Set y-axis limits
  if current_menu != 'loss':
    ax.set_ylim([0, 100])


  # Set the y-ticks
  if current_menu != 'loss':
    ax.set_yticks(np.arange(0, 101, 10)) # Major ticks
    ax.set_yticks(np.arange(0, 101, 5), minor=True) # Minor ticks

  # Set grid style for major and minor ticks
  ax.grid(which='major', linestyle='-', linewidth='0.8', color='grey')
  ax.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
  ax.legend()

  ax.set_title(f'{HOST} Epoch: {numEpoch} ({str(slider_value)}) {current_menu}')


  canvas = FigureCanvasTkAgg(fig, master=root)  
  canvas.draw()
  canvas.get_tk_widget().grid(row=1, column=0, columnspan=4, sticky="nsew")


def change_graph(number):
  global current_graph_number, button1_text
  current_graph_number = number
  button1_text.set('electron' if current_graph_number == 1 else 'etri')
  draw_graph(slider.get())


def change_dropdown(*args):
  global current_menu
  current_menu = menuvar.get()
  draw_graph(slider.get())


def exit_program(event=None):
  root.destroy()

if __name__ == '__main__':

  if github_fetch:
    cprint('Fetch Log Data Files', 'green')
    subprocess.run(["python3", fetch_file])
    cprint('Fetch Done...', 'green')
    
    with open(prev_epoch_file, 'r') as f:
      cprint(f"\nPrev Epochs", "green")
      [print(x.strip()) for x in f.readlines()]

    time.sleep(1)

  file_name = "train_log_main.log"
  etri_data = convert_log(file_name)
  file_name = "train_log_electron.log"
  electron_data = convert_log(file_name)

  with open(prev_epoch_file, 'w') as f:
    electron_epoch = len(electron_data["train"]["iou"])
    etri_epoch = len(etri_data["train"]["iou"])
    f.write(f'electron: {electron_epoch}\n')
    f.write(f'etri: {etri_epoch}\n')
    cprint(f"\nThis Epochs", "green")
    print(f'electron: {electron_epoch}')
    print(f'etri: {etri_epoch}')
  
  root = tk.Tk()

  root.geometry('800x600')

  # Make root window resizable
  root.grid_rowconfigure(1, weight=1)
  root.grid_columnconfigure(0, weight=1)

  # Dropdown menu variable and items
  menuvar = tk.StringVar(root)
  menuitems = {'iou', 'accu', 'loss'}
  # Initial menu item
  menuvar.set('iou') 
  menuvar.trace('w', change_dropdown)

  # Create dropdown menu
  dropdown = tk.OptionMenu(root, menuvar, *menuitems)

  # Button text variable
  button1_text = tk.StringVar()
  button1_text.set('electron' if current_graph_number == 1 else 'etri')

  button1 = tk.Button(root, textvariable=button1_text, command=lambda: change_graph(2 if current_graph_number == 1 else 1))

  exit_button = ttk.Button(root, text="Exit", command=exit_program)

  slider = tk.Scale(root, from_=0.0, to=0.9, resolution=0.1, orient='horizontal', length=200, command=lambda v: draw_graph(v))
  slider.set(.6)

  dropdown.grid(row=0, column=0, padx=100, pady=2, sticky='W')
  slider.grid(row=0, column=0, columnspan=2, padx=55, pady=3)
  button1.grid(row=0, column=1, pady=5)
  exit_button.grid(row=0, column=2, padx=25,  pady=5)

  root.grid_rowconfigure(1, weight=1)
  root.grid_columnconfigure(0, weight=2)
  root.grid_columnconfigure(1, weight=1)
  
  root.bind('q', exit_program)
  root.mainloop()
  

