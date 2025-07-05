from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.course import CourseStatus, EnrollmentStatus

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_hours: Optional[int] = None
    price: int = 0
    is_free: bool = True

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    status: Optional[CourseStatus] = None
    duration_hours: Optional[int] = None
    price: Optional[int] = None
    is_free: Optional[bool] = None

class ModuleBase(BaseModel):
    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    video_url: Optional[str] = None
    order_index: int = 0
    duration_minutes: Optional[int] = None

class ModuleCreate(ModuleBase):
    course_id: int

class ModuleResponse(ModuleBase):
    id: int
    course_id: int
    is_published: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    status: CourseStatus
    created_at: datetime
    modules: List[ModuleResponse] = []

    class Config:
        from_attributes = True

class EnrollmentCreate(BaseModel):
    course_id: int

class EnrollmentResponse(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: EnrollmentStatus
    progress_percentage: int
    enrolled_at: datetime
    course: CourseResponse

    class Config:
        from_attributes = True