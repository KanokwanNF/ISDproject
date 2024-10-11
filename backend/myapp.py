from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from PIL import Image
import numpy as np
import tensorflow as tf
import mysql.connector
from mysql.connector import Error
from datetime import datetime


app = FastAPI()  # สร้างแอพพลิเคชัน FastAPI

# Allow specific origins (update to your frontend URL)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the model once during startup
try:
    model = tf.keras.models.load_model(r"/ISD-pj/backend/mymodel/mymodel_asl.h5") # โหลดโมเดล CNN จากไฟล์
except Exception as e:
    raise RuntimeError(f"Failed to load model: {str(e)}")  

# Function to preprocess the image
def preprocess_image(image_path: str) -> np.ndarray:
    try:
        # เปิดภาพจากไฟล์และทำการปรับขนาด
        image = Image.open(image_path)
        image = image.resize((200, 200))
        image = np.array(image) / 255.0  # Normalize to range [0, 1] เพื่อให้ค่าระดับสีอยู่ในช่วง 0 ถึง 1
        image = np.expand_dims(image, axis=0)  # เพิ่มมิติของ batch
        return image
    except Exception as e:
        raise RuntimeError(f"Failed to preprocess image {image_path}: {str(e)}") 

# Function to create a database connection
def get_db_connection():
    connection = None
    try:
        # สร้างการเชื่อมต่อกับฐานข้อมูล MySQL
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='signlish'
        )
        if connection.is_connected():
            print("MySQL Database connection successful")  # แสดงข้อความเมื่อเชื่อมต่อฐานข้อมูลสำเร็จ
            return connection
    except Error as e:
        print(f"The error '{e}' occurred")  # แสดงข้อความผิดพลาดเมื่อไม่สามารถเชื่อมต่อได้
        return None

@app.get("/task/{task_id}/result")
def get_task_result(task_id: int):
    connection = get_db_connection()  # เชื่อมต่อกับฐานข้อมูล
    cursor = connection.cursor(dictionary=True)
    
    # Query จำนวนครั้งที่ตอบถูกใน task_id นั้น
    cursor.execute("SELECT COUNT(*) as correct_attempts FROM taskresponses WHERE task_id = %s AND is_correct = TRUE", (task_id,))
    correct_attempts = cursor.fetchone()['correct_attempts']
    
    # Query จำนวนครั้งทั้งหมดที่ตอบใน task_id นั้น
    cursor.execute("SELECT COUNT(*) as total_attempts FROM taskresponses WHERE task_id = %s", (task_id,))
    total_attempts = cursor.fetchone()['total_attempts']

    cursor.close()
    connection.close()
    # คำนวณเปอร์เซ็นต์
    percentage_correct = (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
    return {
        "task_id": task_id,
        "correct_attempts": correct_attempts,
        "total_attempts": total_attempts,
        "percentage_correct": percentage_correct
    }

# Mapping of indices to characters
index_to_character = {i: chr(65 + i) for i in range(26)}  # A-Z สร้างแผนที่ตัวอักษร A ถึง Z

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...), word: str = Form(...)):
    uploaded_files = []  # รายการเก็บไฟล์ที่อัปโหลด
    predictions = []  # รายการเก็บผลการพยากรณ์
    expected_characters = list(word)  # แปลงคำเป็นรายการตัวอักษร

    # Fetch tasks from database to get the correct task IDs
    connection = get_db_connection()  # เชื่อมต่อกับฐานข้อมูล
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT id, expected_answer FROM Tasks")  # ดึงข้อมูลจากตาราง Tasks
    tasks = cursor.fetchall()  # ดึงผลลัพธ์ทั้งหมด
    cursor.close()  # ปิด cursor
    connection.close()  # ปิดการเชื่อมต่อ

    task_ids = {task['expected_answer']: task['id'] for task in tasks}  # สร้างแผนที่ตัวอักษรกับ ID ของงาน

    # Process each uploaded file
    for idx, (file, expected_char) in enumerate(zip(files, expected_characters)):
        if expected_char not in task_ids:
            raise HTTPException(status_code=400, detail=f"Expected character '{expected_char}' does not have a corresponding task ID.")  # ส่งข้อความผิดพลาดถ้าไม่มี ID ของงานที่ตรงกัน

        task_id = task_ids[expected_char]  # ใช้ ID ที่ถูกต้อง
        start_time = datetime.now()  # บันทึกเวลาเริ่มต้น

        try:
            # Save the uploaded file
            file_location = f"imagesAPI/image{idx}.jpg"  # กำหนดที่อยู่ในการบันทึกไฟล์
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)  # บันทึกไฟล์ที่อัปโหลด

            # Preprocess the image and make predictions using the model
            preprocessed_image = preprocess_image(file_location)  # ประมวลผลภาพ
            prediction = model.predict(preprocessed_image)  # ทำการพยากรณ์
            predicted_class = np.argmax(prediction, axis=1)[0]  # หาผลลัพธ์ที่ดีที่สุด
            predictions.append(index_to_character[predicted_class])  # เพิ่มผลลัพธ์ในรายการพยากรณ์
            uploaded_files.append(f"image{idx}.jpg")  # เพิ่มชื่อไฟล์ในรายการไฟล์ที่อัปโหลด

            # Check if the prediction is correct
            is_correct = (predictions == expected_characters)  # ตรวจสอบว่าผลลัพธ์ถูกต้องหรือไม่

            # Save result to database
            end_time = datetime.now()  # บันทึกเวลาเสร็จสิ้น
            connection = get_db_connection()  # เชื่อมต่อกับฐานข้อมูล
            cursor = connection.cursor()  # สร้าง cursor ใหม่
            cursor.execute(
                "INSERT INTO taskresponses (task_id, start_time, end_time, is_correct) VALUES (%s, %s, %s, %s)",  # คำสั่ง SQL เพื่อบันทึกผลลัพธ์
                (task_id, start_time, end_time, is_correct)
            )
            connection.commit()  # คอมมิตการเปลี่ยนแปลงในฐานข้อมูล

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))  # ส่งข้อความผิดพลาดถ้ามีข้อผิดพลาดในการประมวลผล
        finally:
            if cursor:
                cursor.close()  # ปิด cursor ถ้ามีการสร้าง
            if connection:
                connection.close()  # ปิดการเชื่อมต่อ

    # Return results
    return {
        "message": "Files uploaded and processed successfully!",  # ส่งข้อความยืนยัน
        "files": uploaded_files,  # ไฟล์ที่อัปโหลด
        "predictions": predictions,  # ส่งรายการผลลัพธ์
        "expected_characters": expected_characters,  # ส่งตัวอักษรที่คาดหวัง
        "result": "[CORRECT]" if is_correct else "[INCORRECT]"  # ส่งผลลัพธ์ว่าถูกต้องหรือไม่
    }

# Mount static files directories
app.mount("/image", StaticFiles(directory="frontend/image"), name="images")
app.mount("/static", StaticFiles(directory="frontend/pages"), name="pages")

# Routes for web pages
@app.get("/")
async def read_index():
    return JSONResponse(content={"message": "Welcome to the API. Go to /static/index.html for the main page."})
@app.get("/popup")
async def read_popup():
    return JSONResponse(content={"message": "Go to /static/popup.html for the popup page."})
@app.get("/aboutus")
async def read_about_us():
    return JSONResponse(content={"message": "Go to /static/aboutus.html for the about us page."})
@app.get("/letstest")
async def read_lets_test():
    return JSONResponse(content={"message": "Go to /static/letstest.html for the lets test page."})
@app.get("/test")
async def read_test():
    return JSONResponse(content={"message": "Go to /static/test.html for the test page."})

# URL references
# Main page: http://127.0.0.1:8000/static/index.html
# Popup: http://127.0.0.1:8000/static/popup.html
# About us: http://127.0.0.1:8000/static/aboutus.html
# Let's test: http://127.0.0.1:8000/static/letstest.html
# Test: http://127.0.0.1:8000/static/test.html
