from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.course import Course
from app.services.ingestion import process_video_rag
from app.core.security import hash_password
from sqlalchemy import select

async def create_seed_data():
    async with AsyncSessionLocal() as db:
        initial_user = (await db.execute(select(User).where(User.email == "instructor@example.com"))).scalar_one_or_none()
        if not initial_user:
            print("🌱 Đang khởi tạo dữ liệu mẫu...")

            # Tạo Giảng viên
            instructor = User(
                email="instructor@example.com",
                hashed_password=hash_password("Instructor123@"),
                full_name="Nguyễn Văn A",
                role=UserRole.INSTRUCTOR
            )
            db.add(instructor)
            await db.commit()
            
            # Tạo Học viên
            student = User(
                email="student@example.com",
                hashed_password=hash_password("Student123@"),
                full_name="Nguyễn Văn B",
                role=UserRole.STUDENT
            )
            db.add(student)
            await db.commit()

            # 2. Tạo Khóa học
            course = Course(
                instructor_id=instructor.id,
                title="Khóa học React & Performance Optimization",
                description="Làm chủ React Hooks, Render Optimization và State Management."
            )
            db.add(course)
            await db.commit()
            
            await db.close()