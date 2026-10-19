from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.course import Course, Lesson
from app.services.ingestion import process_video_rag
from app.core.security import hash_password
from sqlalchemy import select
import asyncio

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
            await db.flush()
            
            # Tạo Học viên
            student = User(
                email="student@example.com",
                hashed_password=hash_password("Student123@"),
                full_name="Nguyễn Văn B",
                role=UserRole.STUDENT
            )
            db.add(student)
            await db.flush()

            # 2. Tạo Khóa học
            course = Course(
                instructor_id=instructor.id,
                title="Khóa học React & Performance Optimization",
                description="Làm chủ React Hooks, Render Optimization và State Management."
            )
            db.add(course)
            await db.flush()

            # 3. Tạo Bài học
            lesson_1 = Lesson(
                course_id=course.id,
                title="Bài 1: useEffect và bài toán Memory Leak",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/v1792081965/test_video_1.mp4",
                duration_seconds=360,
                order_index=1
            )
            
            lesson_2 = Lesson(
                course_id=course.id,
                title="Bài 2: useState và bài toán State Management",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/v1792081969/test_video_2.mp4",
                duration_seconds=360,
                order_index=2
            )
            
            lesson_3 = Lesson(
                course_id=course.id,
                title="Bài 3: So sánh useMemo và useCallback khác nhau gì?",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/v1792082183/test_video_3.mp4",
                duration_seconds=360,
                order_index=3
            )
            
            lesson_4 = Lesson(
                course_id=course.id,
                title="Bài 4: useRef() hook | Cách sử dụng useRef() hook",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/v1792081963/test_video_4.mp4",
                duration_seconds=360,
                order_index=4
            )
            db.add_all([lesson_1, lesson_2, lesson_3, lesson_4])
            await db.flush()

            print("🧠 Đang chunking transcript và tạo embeddings vào PostgreSQL...")
            await process_video_rag(course_id=course.id, lesson_id=lesson_1.id, video_url=lesson_1.video_url)
            await process_video_rag(course_id=course.id, lesson_id=lesson_2.id, video_url=lesson_2.video_url)
            await process_video_rag(course_id=course.id, lesson_id=lesson_3.id, video_url=lesson_3.video_url)
            await process_video_rag(course_id=course.id, lesson_id=lesson_4.id, video_url=lesson_4.video_url)

            await db.close()

            print(f"✅ Hoàn tất! Đã lưu thành công:")


if __name__ == "__main__":
    asyncio.run(create_seed_data())