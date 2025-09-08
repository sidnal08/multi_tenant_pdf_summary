import os
from app.config import UPLOAD_FOLDER

def save_file(file_obj, filename):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    with open(file_path, "wb") as f:
        f.write(file_obj)
    return file_path