import os
import shutil
from fastapi import UploadFile, HTTPException
from typing import Optional
import uuid
from pathlib import Path

# Configuration
UPLOAD_DIR = Path("uploads")
SUBMISSIONS_DIR = UPLOAD_DIR / "submissions"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt", ".zip", ".jpg", ".jpeg", ".png", ".gif"}

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
SUBMISSIONS_DIR.mkdir(exist_ok=True)

def validate_file(file: UploadFile) -> bool:
    """ตรวจสอบไฟล์ที่อัปโหลด"""
    if not file.filename:
        return False
    
    # ตรวจสอบขนาดไฟล์
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size too large (max {MAX_FILE_SIZE // (1024*1024)}MB)")
    
    # ตรวจสอบ extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return True

def save_submission_file(file: UploadFile, assignment_id: int, student_id: int) -> tuple[str, str]:
    """บันทึกไฟล์ submission และส่งคืน file_url และ file_path"""
    if not validate_file(file):
        raise HTTPException(status_code=400, detail="Invalid file")
    
    # สร้างชื่อไฟล์ที่ unique
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{assignment_id}_{student_id}_{uuid.uuid4().hex[:8]}{file_ext}"
    
    # สร้างเส้นทางไฟล์
    file_path = SUBMISSIONS_DIR / unique_filename
    
    try:
        # บันทึกไฟล์
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # สร้าง URL สำหรับเข้าถึงไฟล์
        file_url = f"/uploads/submissions/{unique_filename}"
        
        return file_url, str(file_path)
        
    except Exception as e:
        # ลบไฟล์ถ้าเกิดข้อผิดพลาด
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

def delete_submission_file(file_url: str) -> bool:
    """ลบไฟล์ submission"""
    try:
        if file_url.startswith("/uploads/submissions/"):
            filename = file_url.split("/")[-1]
            file_path = SUBMISSIONS_DIR / filename
            if file_path.exists():
                file_path.unlink()
                return True
        return False
    except Exception:
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """ดูข้อมูลไฟล์"""
    try:
        path = Path(file_path)
        if path.exists():
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "extension": path.suffix.lower()
            }
        return None
    except Exception:
        return None