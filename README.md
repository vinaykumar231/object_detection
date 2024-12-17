# Object Detection and Analysis API

## Overview

This project is an API built using FastAPI that allows users to upload images and videos for object detection and analysis. The API utilizes a generative AI model to identify and count objects within the media files, returning structured JSON responses with detailed information about the detected objects.

## Features

- **Image and Video Upload**: Users can upload images and videos for analysis.
- **Object Detection**: The API detects and counts objects in the uploaded media.
- **Bounding Box Information**: For each detected object, the API provides bounding box coordinates.
- **General Description**: A brief summary of the detected objects in the media is included in the response.
- **Database Integration**: All uploads and detection results are stored in a MySQL database.

## Technologies Used

- **FastAPI**: A modern web framework for building APIs with Python.
- **SQLAlchemy**: An ORM for database interactions.
- **Pillow**: A Python Imaging Library for image processing.
- **Google Generative AI**: Used for object detection and analysis.
- **MySQL**: The database used for storing media uploads and detection results.
- **Python-dotenv**: For managing environment variables.

## Installation

### Prerequisites

- Python 3.7 or higher
- MySQL server
- Virtual environment (recommended)

### Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**: Create a `.env` file in the root directory and add the following variables:
   ```plaintext
   DB_HOST=<your_database_host>
   DB_PORT=<your_database_port>
   DB_USER=<your_database_user>
   DB_PASSWORD=<your_database_password>
   DB_NAME=<your_database_name>
   GEMINI_API_KEY=<your_gemini_api_key>
   ```

5. **Create the database schema**: Ensure that the necessary tables are created in your MySQL database. You can use the provided SQL scripts or manually create the tables based on the models defined in `app/models/models.py`.

## Usage

### Running the API

To start the FastAPI server, run the following command:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Endpoints

#### Upload Images

- **Endpoint**: `/detection/images`
- **Method**: `POST`
- **Request**: 
  - `media_files`: List of image files to upload.
  - `task_id`: An integer representing the task ID (default is 5250).

- **Response**: JSON object containing the results of the analysis.

#### Upload Videos

- **Endpoint**: `/detection/video`
- **Method**: `POST`
- **Request**: 
  - `media_file`: The video file to upload.
  - `task_id`: An integer representing the task ID (default is 5250).

- **Response**: JSON object containing the results of the analysis.

## Database Schema

The project uses the following database tables:

1. **media_upload**: Stores metadata about uploaded media files.
2. **detection_results**: Stores results of the object detection analysis.
3. **detected_objects**: Stores individual detected objects with their bounding box coordinates.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- Thanks to the FastAPI community for their excellent documentation and support.
- Special thanks to the developers of the Google Generative AI model for their contributions to AI and machine learning.
