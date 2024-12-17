import json
from google.generativeai import GenerativeModel, upload_file, get_file, delete_file
import google.generativeai as genai
# from app.services.database import (insert_media,insert_detection_results, insert_detected_objects,)
from PIL import Image
import os
from app.services.prompt_generator import general_prompt, general_video_prompt
import time
from app.services.get_task import fetch_task_by_id
from fastapi import HTTPException
from app.services.draw_bounding_boxes import draw_bounding_boxes
import uuid
from dotenv import load_dotenv
from ..models import MediaUpload, DetectionResults, DetectedObjects
from ..database import get_db
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from ..database import  get_db, SessionLocal
import logging

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

GENERATION_CONFIG = {
    "temperature": 0,
    "top_p": 0.8,
    "top_k": 128,
    "max_output_tokens": 4096,
    "response_mime_type": "application/json",
}

UPLOAD_DIR_BOUNDING_BOX_IMG = "static/uploads/bounding_box_images/"
os.makedirs(UPLOAD_DIR_BOUNDING_BOX_IMG, exist_ok=True)


################################################### IMAGE PROCESSING ###################################################

async def process_image(file_path, media_type, task_id , db: SessionLocal): # type: ignore

    try:
        task_data = await fetch_task_by_id(task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_type = task_data["task_type"]
    unit_id = task_data["unit_id"]
    property_id = task_data["property_id"]

    upload_db = MediaUpload(
        task_type=task_type,
        unit_id=unit_id,
        property_id=property_id,
        media_type=media_type,
        media_url=file_path,
    )
    db.add(upload_db)
    db.flush()
    db.refresh(upload_db) 
    upload_id_value = upload_db.upload_id 

    with open(file_path, "rb") as image_file:
        image = Image.open(image_file)
        model = GenerativeModel(
            model_name="models/gemini-1.5-pro", generation_config=GENERATION_CONFIG
        )
        response = model.generate_content([general_prompt, image])

    response_json = json.loads(response.text)
    # print(response_json)

    detected_items = {}

    for obj in response_json["objects"]:
        if isinstance(obj, dict):
            label = obj.get("label", "Unknown")  
            bounding_box = obj.get("bounding_box", {})
            detected_items[label] = detected_items.get(label, 0) + 1
        else:
            print("Invalid object structure:", obj)

    image_with_bounding_boxes = draw_bounding_boxes(
        file_path=file_path, bounding_boxes=response_json["objects"]
    )
    unique_filename = f"bounding_box_{uuid.uuid4()}.png"
    save_path_bounding_box_img = os.path.join(
        UPLOAD_DIR_BOUNDING_BOX_IMG, unique_filename
    )
    image_with_bounding_boxes.save(save_path_bounding_box_img)

    result_db = DetectionResults(
        upload_id=upload_id_value,
        detected_items=detected_items,
        detected_count=len(response_json["objects"]),
        bounding_box_summary=response_json,
        image_with_bounding_box_url=save_path_bounding_box_img,
    )
    db.add(result_db)
    db.flush()
    db.refresh(result_db)

    all_data = []
    for obj in response_json["objects"]:
        bounding_box = obj.get("bounding_box", [])
        if len(bounding_box) == 4:  
            ymin, xmin, ymax, xmax = bounding_box
        else:
            ymin = xmin = ymax = xmax = 0  
        
        detect_db = DetectedObjects(
            result_id=result_db.result_id,
            label=obj.get("label", "Unknown"),
            ymin=ymin,
            xmin=xmin,
            ymax=ymax,
            xmax=xmax,
        )
        all_data.append(detect_db)

    db.add_all(all_data)
    db.commit()

    return {
        "detected_count": len(response_json["objects"]),
        "response_json": response_json,  
         
    }

######################################################### process_video ############################################

async def process_video(file_path, media_type, task_id,  db:Session=Depends(get_db)):

    try:
        task_data = await fetch_task_by_id(task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    task_type = task_data["task_type"]
    unit_id = task_data["unit_id"]
    property_id = task_data["property_id"]

    upload_db = MediaUpload(
        task_type=task_type,
        unit_id=unit_id,
        property_id=property_id,
        media_type=media_type,
        media_url=file_path,
    )
    db.add(upload_db)
    db.commit()
    db.refresh(upload_db)
    
    video_upload = upload_file(path=file_path, mime_type="video/mp4")
    while video_upload.state.name == "PROCESSING":
        time.sleep(10)
        video_upload = get_file(video_upload.name)

    if video_upload.state.name == "FAILED":
        raise Exception("Video processing failed.")

    model = GenerativeModel(
        model_name="models/gemini-1.5-pro", generation_config=GENERATION_CONFIG
    )
    response = model.generate_content([general_video_prompt, video_upload])
    delete_file(video_upload.name)

    response_json = json.loads(response.text)

    result_db = DetectionResults(
        upload_id=upload_db.upload_id,
        detected_items=response_json["visible_objects"],
        detected_count=sum(response_json["visible_objects"].values()),
        bounding_box_summary=response_json,
    )
    db.add(result_db)
    db.commit()
    db.refresh(result_db)

    return {
        "detected_count": result_db.detected_count,
        "response_json": response_json,  
         
    }

