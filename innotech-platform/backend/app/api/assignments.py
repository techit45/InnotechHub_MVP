from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..database import get_db
from ..models.user import User, UserRole
from ..models.course import Course
from ..models.assignment import Assignment, Submission, SubmissionStatus
from ..schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse, AssignmentWithSubmissions,
    SubmissionCreate, SubmissionUpdate, SubmissionResponse, SubmissionWithAssignment
)
from ..utils.auth import get_current_user
from ..utils.file_handler import save_submission_file, delete_submission_file

router = APIRouter(prefix="/assignments", tags=["assignments"])

# Assignment Management Endpoints

@router.post("/", response_model=AssignmentResponse)
async def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """สร้างงานที่มอบหมาย (สำหรับ trainer และ admin เท่านั้น)"""
    if current_user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can create assignments"
        )
    
    # ตรวจสอบว่ามีหลักสูตรนี้อยู่จริง
    course = db.query(Course).filter(Course.id == assignment.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # ตรวจสอบว่า trainer สามารถสร้าง assignment ในหลักสูตรนี้ได้
    if current_user.role == UserRole.TRAINER and course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create assignments for your own courses"
        )
    
    db_assignment = Assignment(**assignment.model_dump())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    # Add submissions_count
    db_assignment.submissions_count = 0
    
    return db_assignment

@router.get("/", response_model=List[AssignmentResponse])
async def get_assignments(
    course_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ดูรายการงานที่มอบหมาย"""
    query = db.query(Assignment)
    
    if course_id:
        query = query.filter(Assignment.course_id == course_id)
        
        # ตรวจสอบว่าผู้ใช้มีสิทธิ์เข้าถึงหลักสูตรนี้
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found"
            )
    
    assignments = query.offset(skip).limit(limit).all()
    
    # Add submissions count for each assignment
    for assignment in assignments:
        assignment.submissions_count = db.query(Submission).filter(
            Submission.assignment_id == assignment.id
        ).count()
    
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentWithSubmissions)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ดูรายละเอียดงานที่มอบหมาย"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # ดูรายการ submissions (เฉพาะ trainer/admin ที่เป็นเจ้าของหลักสูตร)
    if current_user.role in [UserRole.TRAINER, UserRole.ADMIN]:
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if current_user.role == UserRole.TRAINER and course.instructor_id != current_user.id:
            # ถ้าเป็น trainer แต่ไม่ใช่เจ้าของหลักสูตร ให้ดู assignment เฉยๆ
            assignment.submissions = []
        else:
            # ดูได้ทุก submissions
            submissions = db.query(Submission).filter(Submission.assignment_id == assignment_id).all()
            assignment.submissions = submissions
    else:
        # ถ้าเป็น student ให้ดูเฉพาะ submission ของตัวเอง
        user_submission = db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == current_user.id
        ).first()
        assignment.submissions = [user_submission] if user_submission else []
    
    assignment.submissions_count = len(assignment.submissions)
    return assignment

@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    assignment_update: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """แก้ไขงานที่มอบหมาย"""
    if current_user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can update assignments"
        )
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # ตรวจสอบสิทธิ์
    if current_user.role == UserRole.TRAINER:
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update assignments for your own courses"
            )
    
    # อัปเดตเฉพาะฟิลด์ที่ส่งมา
    update_data = assignment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)
    
    assignment.submissions_count = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    ).count()
    
    return assignment

@router.delete("/{assignment_id}")
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ลบงานที่มอบหมาย"""
    if current_user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainers and admins can delete assignments"
        )
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # ตรวจสอบสิทธิ์
    if current_user.role == UserRole.TRAINER:
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete assignments for your own courses"
            )
    
    db.delete(assignment)
    db.commit()
    
    return {"message": "Assignment deleted successfully"}

# Submission Management Endpoints

@router.post("/{assignment_id}/submissions", response_model=SubmissionResponse)
async def create_submission(
    assignment_id: int,
    content: str = Form(None),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ส่งงาน"""
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can submit assignments"
        )
    
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # ตรวจสอบว่าส่งงานแล้วหรือยัง
    existing_submission = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == current_user.id
    ).first()
    
    if existing_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted this assignment"
        )
    
    # ตรวจสอบว่ามี content หรือ file
    if not content and not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide either content or file"
        )
    
    # จัดการไฟล์
    file_url = None
    file_name = None
    if file:
        file_name = file.filename
        try:
            file_url, file_path = save_submission_file(file, assignment_id, current_user.id)
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    db_submission = Submission(
        assignment_id=assignment_id,
        student_id=current_user.id,
        content=content,
        file_url=file_url,
        file_name=file_name,
        status=SubmissionStatus.SUBMITTED
    )
    
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    return db_submission

@router.get("/{assignment_id}/submissions", response_model=List[SubmissionResponse])
async def get_submissions(
    assignment_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ดูรายการ submissions"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    query = db.query(Submission).filter(Submission.assignment_id == assignment_id)
    
    # ตรวจสอบสิทธิ์
    if current_user.role == UserRole.STUDENT:
        # Student ดูได้เฉพาะ submission ของตัวเอง
        query = query.filter(Submission.student_id == current_user.id)
    elif current_user.role == UserRole.TRAINER:
        # Trainer ดูได้เฉพาะหลักสูตรของตัวเอง
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view submissions for your own courses"
            )
    
    submissions = query.offset(skip).limit(limit).all()
    return submissions

@router.put("/submissions/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: int,
    submission_update: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """อัปเดต submission (ให้คะแนนและฟีดแบ็ก)"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # ตรวจสอบสิทธิ์
    if current_user.role == UserRole.STUDENT:
        # Student แก้ได้เฉพาะ content ของตัวเอง และยังไม่ submit
        if submission.student_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own submissions"
            )
        if submission.status != SubmissionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update submitted assignment"
            )
        # Student แก้ได้เฉพาะ content
        if submission_update.content is not None:
            submission.content = submission_update.content
    
    elif current_user.role in [UserRole.TRAINER, UserRole.ADMIN]:
        # Trainer/Admin ให้คะแนนและฟีดแบ็ก
        if current_user.role == UserRole.TRAINER:
            assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
            course = db.query(Course).filter(Course.id == assignment.course_id).first()
            if course.instructor_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only grade submissions for your own courses"
                )
        
        # อัปเดตการให้คะแนน
        update_data = submission_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(submission, field, value)
        
        if submission_update.status or submission_update.score is not None or submission_update.feedback:
            submission.reviewed_at = datetime.utcnow()
            if submission_update.status:
                submission.status = SubmissionStatus(submission_update.status)
    
    db.commit()
    db.refresh(submission)
    
    return submission

@router.get("/submissions/{submission_id}", response_model=SubmissionWithAssignment)
async def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """ดูรายละเอียด submission"""
    submission = db.query(Submission).filter(Submission.id == submission_id).first()
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    # ตรวจสอบสิทธิ์
    if current_user.role == UserRole.STUDENT and submission.student_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own submissions"
        )
    elif current_user.role == UserRole.TRAINER:
        assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
        course = db.query(Course).filter(Course.id == assignment.course_id).first()
        if course.instructor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view submissions for your own courses"
            )
    
    return submission