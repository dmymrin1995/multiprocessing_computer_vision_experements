import pandas as pd
import os
from pathlib import Path
from ultralytics import YOLO


def run_tracking_in_process(filepath):
    data_list = []
    filename_save = os.path.splitext(filepath[0])[0]
    csv_output = Path(f"./output/{filename_save}_csv_output")
    csv_output.mkdir(parents=True, exist_ok=True)

    model_1 = YOLO("yolov8n.pt")
    results = model_1.track(filepath, save=True, stream=True)

    for frame, r in enumerate(results):
        ids = r.boxes.id.int().cpu().tolist()
        clses = r.boxes.cls.int().cpu().tolist()
        boxes = r.boxes.xywh.cpu()

        for obj_id, obj_cls, box in zip(ids, clses, boxes):
            data_list.append(
                {"frame": frame, "obj_id": obj_id, "clses": clses, "boxes": boxes}
            )

    output_data = pd.DataFrame(data_list)
    outputcsv_save_path = os.path.join(csv_output, f"{filename_save}_tracking.scv")
    output_data.to_csv(outputcsv_save_path)

    return outputcsv_save_path, filepath
