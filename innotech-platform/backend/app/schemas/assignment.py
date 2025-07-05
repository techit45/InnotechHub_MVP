from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class AssignmentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: int = Field(default=100, ge=0, le=1000)
    due_date: Optional[datetime] = None
    is_required: bool = True

class AssignmentCreate(AssignmentBase):
    course_id: int

class AssignmentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    instructions: Optional[str] = None
    max_score: Optional[int] = Field(None, ge=0, le=1000)
    due_date: Optional[datetime] = None
    is_required: Optional[bool] = None

class AssignmentResponse(AssignmentBase):
    id: int
    course_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    submissions_count: Optional[int] = 0

    class Config:
        from_attributes = True

class SubmissionBase(BaseModel):
    content: Optional[str] = None
    file_name: Optional[str] = None

class SubmissionCreate(SubmissionBase):
    assignment_id: int

class SubmissionUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    score: Optional[int] = Field(None, ge=0)
    feedback: Optional[str] = None

class SubmissionResponse(SubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    file_url: Optional[str] = None
    status: str
    score: Optional[int] = None
    feedback: Optional[str] = None
    submitted_at: datetime
    reviewed_at: Optional[datetime] = None
    student: Optional[UserResponse] = None

    class Config:
        from_attributes = True

class SubmissionWithAssignment(SubmissionResponse):
    assignment: Optional[AssignmentResponse] = None

class AssignmentWithSubmissions(AssignmentResponse):
    submissions: List[SubmissionResponse] = []