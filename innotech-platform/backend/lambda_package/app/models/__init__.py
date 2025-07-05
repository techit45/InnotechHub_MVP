# Import all models here for easy access
from .user import User
from .course import Course, Module, Enrollment
from .assignment import Assignment, Submission

__all__ = [
    "User",
    "Course", 
    "Module",
    "Enrollment",
    "Assignment",
    "Submission"
]