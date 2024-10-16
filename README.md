# Sign Language Class Website - ISDproject (ﾉ◕ヮ◕)ﾉ*:･ﾟ
by 65070006(nf), 65070167(np)


## Description
The **Sign Language Class Website** is an interactive application designed to recognize American Sign Language (ASL) from images. Users can upload images of hand signs, which the application processes using deep learning techniques. It provides immediate feedback on whether the sign corresponds to the intended letter, making it an engaging and effective tool for learning ASL.

## Directory Structure
The project is organized into a clear directory structure to facilitate easy navigation and maintenance. Below is a breakdown of the important directories and files:

### Backend

- **mymodel/**
  - This folder contains the following:
    1. **dataset/**: This subfolder holds the datasets used for training and testing the models.
    2. **model/**: This subfolder includes the trained model files that are utilized for inference and predictions.
- **myapp.py**: 
  - This is the main application file containing the FastAPI implementation for the API. It handles incoming requests, processes images, and communicates with the database.

### Frontend

- **images/**: 
  - This folder contains images used for displaying on the web pages. It includes all the visual assets that enhance the user interface and experience.
- **pages/**: 
  - This folder contains various HTML files that make up the different web pages of the application:
    1. **index.html**: The main landing page of the website.
    2. **popup.html**: A page for displaying pop-up notifications and messages.
    3. **aboutus.html**: A page providing information about the project and the team behind it.
    4. **letstest.html**: A page showcasing the latest updates or features of the application.
    5. **test.html**: A page for testing functionalities and user interactions.
       
### hand_test
  - This folder is used to store hand images that serve as input during the testing phase of the application. It allows for easy access to specific hand images for testing sign language recognition functionalities.

### imagesAPI 
  - directory serves as a storage location for the uploaded images, facilitating organized management of the images and ensuring easy access for processing and analysis.

## Prerequisites
- **Python 3.8 or later**
- **Required Libraries**:
  - FastAPI
  - TensorFlow
  - Pillow
  - NumPy
  - mysql-connector-python
  - CORS Middleware for FastAPI

## Requirements
Before running the application, make sure you have the following libraries installed. You can use the provided commands to install them.
To install the required libraries, you can use the following command:
```bash
pip install fastapi
pip install tensorflow
pip install pillow
pip install numpy
pip install mysql-connector-python
```

### Setting Up a Virtual Environment (Optional)
1. Create a virtual environment:
   
   `python -m venv venv`

2. Activate the virtual environment:
   - On Windows:
   
     `venv\Scripts\activate`

   - On macOS/Linux:
   
     `source venv/bin/activate`

## Running the Application
1. Navigate to the project directory.
2. Start the FastAPI application using the following command:

   `uvicorn myapp:app --reload`

3. Open your browser and go to `http://127.0.0.1:8000/docs` to view the interactive API documentation.

## How to Use
### Uploading Images
- Users can upload images of hand signs using the provided frontend interface.
- The website allows users to upload images in two ways:
1. **From the Device**: You can select an image file directly from your computer.
2. **Using the Camera**: You can capture a photo using your device's camera and upload it instantly.

### Image Processing
- Each uploaded image is preprocessed (resized and normalized) before being passed to the deep learning model for prediction.
- The model predicts the corresponding character for each sign.

### Results
- The website will return whether the predicted characters match the expected characters.
- Results are saved in a MySQL database for further analysis.

## Important Endpoints
- **Upload Images**: `POST /upload`
- **Get Task Result**: `GET /task/{task_id}/result`
- **Welcome Message**: `GET /`

### URL References
- Main page: `http://127.0.0.1:8000/static/index.html`
- Popup page: `http://127.0.0.1:8000/static/popup.html`
- About us page: `http://127.0.0.1:8000/static/aboutus.html`
- Let's test page: `http://127.0.0.1:8000/static/letstest.html`
- Test page: `http://127.0.0.1:8000/static/test.html`

## Database Connection
### Tables
- **Tasks Table**:
  - `id` (INT, primary key)
  - `expected_answer` (VARCHAR)
  
- **TaskResponses Table**:
  - `id` (INT, primary key)
  - `task_id` (INT, foreign key)
  - `start_time` (DATETIME)
  - `end_time` (DATETIME)
  - `is_correct` (BOOLEAN)

## Summary
The **Sign Language Website** aims to provide an interactive way to learn ASL through image recognition. We encourage contributions and suggestions to enhance the application's capabilities. For any inquiries, please contact us. **"Thank you ♡"**
