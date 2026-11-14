import uuid
from fastapi import APIRouter
from app.schemas.course import CourseDetailResponse, CourseListItem
from app.services.courses import CourseService
from app.core.dependencies import DBSession
from app.core.exceptions import CourseNotFoundException

router = APIRouter(
    prefix="/courses", 
    tags=["Courses"]
)


@router.get("", response_model=list[CourseListItem])
async def get_courses(db: DBSession):
    """Lấy danh sách tất cả các khóa học"""
    return await CourseService.get_courses(db)


@router.get("/{course_id}", response_model=CourseDetailResponse)
async def get_course_detail(course_id: uuid.UUID, db: DBSession):
    """Lấy chi tiết khóa học kèm danh sách bài học"""
    course = await CourseService.get_course_detail(course_id, db)

    if not course:
        raise CourseNotFoundException()

    return course
