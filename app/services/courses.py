from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.models.course import Course
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

class CourseService():
    
    @staticmethod
    async def get_courses(db: AsyncSession):
        """Lấy danh sách tất cả các khóa học"""
        stmt = select(Course).order_by(Course.created_at.desc())
        return (await db.execute(stmt)).scalars().all()

    @staticmethod
    async def get_course_detail(course_id: uuid.UUID, db: AsyncSession):
        """Lấy chi tiết khóa học kèm danh sách bài học"""
        stmt = (
            select(Course)
            .options(selectinload(Course.lessons))
            .where(Course.id == course_id)
        )
        return (await db.execute(stmt)).scalar_one_or_none()
