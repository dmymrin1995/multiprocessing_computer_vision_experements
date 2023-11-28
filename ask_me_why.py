import multiprocessing
import time

from glob import glob


# Определение функции для трекинга видео
def track_video(track_queue, process_queue, video_list):
    while True:
        if not track_queue.empty():  # Если есть видео для трекинга
            video = track_queue.get()  # Получаем видео из очереди
            print(f"Начат трекинг видео {video}")
            # Тут можно вызвать функцию для трекинга видео
            time.sleep(5)  # Здесь можно добавить свою логику трекинга
            print(f"Завершен трекинг видео {video}")
            process_queue.put(video)  # Передаем видео в очередь для обработки
        else:
            time.sleep(1)


# Определение функции для записи преобразований
def process_video(process_queue, recording_queue):
    while True:
        if not process_queue.empty():  # Если есть видео для обработки
            video = process_queue.get()  # Получаем видео из очереди
            print(f"Начата запись преобразований для видео {video}")
            # Тут можно вызвать функцию для записи преобразований
            time.sleep(5)  # Здесь можно добавить свою логику обработки
            print(f"Завершена запись преобразований для видео {video}")
            recording_queue.put(video)  # Передаем видео в очередь для записи
        else:
            time.sleep(1)


if __name__ == "__main__":
    track_queue = multiprocessing.Queue()
    process_queue = multiprocessing.Queue()
    recording_queue = multiprocessing.Queue()

    files = glob(r"./videos/**/*.*", recursive=True)
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
