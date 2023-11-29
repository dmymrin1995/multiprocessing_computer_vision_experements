import cv2
import os
import torch
# import torch.multiprocessing as multiprocessing

import pandas as pd
from ultralytics import YOLO
from glob import glob
from IPython.display import clear_output
from pathlib import Path


import multiprocessing
import time

def run_tracking(filepath):
  data_list = []
  filename_save = os.path.splitext(filepath)[0].split("/")[-1]

  csv_output = Path(f"./output/{filename_save}_csv_output")
  csv_output.mkdir(parents=True, exist_ok=True)

  model_1 = YOLO('yolov8n.pt')
  # model_1.to(device)
  results = model_1.track(filepath, stream=True)

  for frame, r in enumerate(results):
      ids = r.boxes.id.int().cpu().tolist()
      clses = r.boxes.cls.int().cpu().tolist()
      boxes = r.boxes.xywh.cpu()

      for obj_id, obj_cls, box in zip(ids, clses, boxes):
        data_list.append({"frame": frame,
                          "obj_id": obj_id,
                          "clses": clses,
                          "boxes": boxes})
      clear_output()

  output_data = pd.DataFrame(data_list)
  outputcsv_save_path = os.path.join(csv_output, f"{filename_save}.scv")
  output_data.to_csv(outputcsv_save_path, sep="^", encoding='utf-8')
  return outputcsv_save_path, filepath

def get_frame(path_to_csv):
  return pd.read_csv(path_to_csv, sep="^", encoding='utf-8')

def run_recording(output_csv, video_file):
  frame = get_frame(output_csv)
  
  cap = cv2.VideoCapture(video_file)
  
  while cap.isOpened():
    
    ret, frame = cap.read()
  
    if ret == True:
      print(frame)
    else:
      break
  
  cap.release()
  cv2.destroyAllWindows()


# Определение функции для трекинга видео
def track_video(track_queue, process_queue, video_list):
    while True:
        if not track_queue.empty():  # Если есть видео для трекинга
            video = track_queue.get()  # Получаем видео из очереди
            print(f"Начат трекинг видео {video}")
            tracking_out = run_tracking(video)
            # Тут можно вызвать функцию для трекинга видео
            time.sleep(5)  # Здесь можно добавить свою логику трекинга
            print(f"Завершен трекинг видео {video}")
            process_queue.put(tracking_out)  # Передаем видео в очередь для обработки
        else:
            time.sleep(1)


# Определение функции для записи преобразований
def process_video(process_queue, recording_queue):
    while True:
        if not process_queue.empty():  # Если есть видео для обработки
            csv, video = process_queue.get()  # Получаем видео из очереди
            print(f"Начата запись преобразований для видео {video}")
            run_recording(csv, video)# Тут можно вызвать функцию для записи преобразований
            time.sleep(5)  # Здесь можно добавить свою логику обработки
            print(f"Завершена запись преобразований для видео {video}")
            recording_queue.put(video)  # Передаем видео в очередь для записи
        else:
            time.sleep(1)




if __name__ == "__main__":
  torch.multiprocessing.set_start_method('spawn')
  
  if torch.cuda.is_available():
    device = torch.device("cuda")
  else:
    device = torch.device("cpu")

  track_queue = multiprocessing.Queue()
  process_queue = multiprocessing.Queue()
  recording_queue = multiprocessing.Queue()

  files = glob(r"./video/**/*.*", recursive=True)
  video_list = [file for file in files if file.endswith((".mp4", ".avi", ".mov"))]
  print(video_list)

  track_process = multiprocessing.Process(
      target=track_video, args=(track_queue, process_queue, video_list)
  )
  process_process = multiprocessing.Process(
      target=process_video, args=(process_queue, recording_queue)
  )

  track_process.start()
  process_process.start()

  for video in video_list:
      track_queue.put(video)

  track_process.join()
  process_process.join()
