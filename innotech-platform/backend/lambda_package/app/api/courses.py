from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.user import User, UserRole
from ..models.course import Course, Module, Enrollment, CourseStatus, EnrollmentStatus
from ..schemas.course import (
    CourseCreate, CourseUpdate, CourseResponse,
    ModuleCreate, ModuleResponse,
    EnrollmentCreate, EnrollmentResponse
)
from ..utils.auth import get_current_active_user

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("/", response_model=List[CourseResponse])
def get_courses(
    skip: int = 0, 
    limit: int = 100,
    status: CourseStatus = None,
    db: Session = Depends(get_db)
):
    """ดูรายการหลักสูตรทั้งหมด"""
    query = db.query(Course)
    
    # กรองเฉพาะหลักสูตรที่เผยแพร่แล้ว (สำหรับผู้ใช้ทั่วไป)
    query = query.filter(Course.status == CourseStatus.PUBLISHED)
    
    if status:
        query = query.filter(Course.status == status)
    
    courses = query.offset(skip).limit(limit).all()
    return courses

@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """ดูรายละเอียดหลักสูตร"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # ตรวจสอบว่าหลักสูตรเผยแพร่แล้ว
    if course.status != CourseStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not available"
        )
    
    return course

@router.post("/", response_model=CourseResponse)
def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """สร้างหลักสูตรใหม่ (สำหรับ trainer/admin)"""
    if current_user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create course"
        )
    
    new_course = Course(
        **course_data.dict(),
        instructor_id=current_user.id
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course

@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """แก้ไขหลักสูตร"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # ตรวจสอบสิทธิ์: เจ้าของหลักสูตรหรือ admin
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # อัปเดตข้อมูล
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)
    
    db.commit()
    db.refresh(course)
    
    return course

@router.delete("/{course_id}")
def delete_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ลบหลักสูตร"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # ตรวจสอบสิทธิ์: เจ้าของหลักสูตรหรือ admin
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(course)
    db.commit()
    
    return {"message": "Course deleted successfully"}

# Enrollment endpoints
@router.post("/{course_id}/enroll", response_model=EnrollmentResponse)
def enroll_course(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ลงทะเบียนเรียนหลักสูตร"""
    # ตรวจสอบหลักสูตร
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if course.status != CourseStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course is not available for enrollment"
        )
    
    # ตรวจสอบการลงทะเบียนซ้ำ
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already enrolled in this course"
        )
    
    # สร้างการลงทะเบียนใหม่
    new_enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    
    return new_enrollment

@router.get("/my/enrollments", response_model=List[EnrollmentResponse])
def get_my_enrollments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ดูหลักสูตรที่ลงทะเบียนไว้"""
    enrollments = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id
    ).all()
    
    return enrollments

# Module endpoints
@router.post("/{course_id}/modules", response_model=ModuleResponse)
def create_module(
    course_id: int,
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """สร้างบทเรียนในหลักสูตร"""
    # ตรวจสอบหลักสูตร
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # ตรวจสอบสิทธิ์
    if course.instructor_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # สร้างบทเรียนใหม่
    new_module = Module(
        **module_data.dict(),
        course_id=course_id
    )
    
    db.add(new_module)
    db.commit()
    db.refresh(new_module)
    
    return new_module

@router.get("/{course_id}/modules", response_model=List[ModuleResponse])
def get_course_modules(
    course_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """ดูบทเรียนในหลักสูตร"""
    # ตรวจสอบการลงทะเบียน
    enrollment = db.query(Enrollment).filter(
        Enrollment.user_id == current_user.id,
        Enrollment.course_id == course_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not enrolled in this course"
        )
    
    modules = db.query(Module).filter(
        Module.course_id == course_id,
        Module.is_published == True
    ).order_by(Module.order_index).all()
    
    return modules