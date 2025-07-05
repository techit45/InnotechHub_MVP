from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class CourseStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    thumbnail_url = Column(String(500))
    instructor_id = Column(Integer, ForeignKey("users.id"))
    status = Column(Enum(CourseStatus), default=CourseStatus.DRAFT)
    duration_hours = Column(Integer)
    price = Column(Integer, default=0)  # ราคาเป็นสตางค์
    is_free = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    instructor = relationship("User", back_populates="courses_created")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")

class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    content = Column(Text)  # เนื้อหาบทเรียน (markdown/html)
    video_url = Column(String(500))
    order_index = Column(Integer, default=0)
    duration_minutes = Column(Integer)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    course = relationship("Course", back_populates="modules")

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    status = Column(Enum(EnrollmentStatus), default=EnrollmentStatus.ACTIVE)
    progress_percentage = Column(Integer, default=0)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")