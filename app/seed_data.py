from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.course import Course, Lesson
from app.services.chunking import TranscriptSegment
from app.services.ingestion import ingest_lesson_transcript
from app.core.security import hash_password
from sqlalchemy import select
from app.core.config import settings
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
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/f_auto,q_auto/v1792081965/test_video_1.mp4",
                duration_seconds=360,
                order_index=1
            )
            
            lesson_2 = Lesson(
                course_id=course.id,
                title="Bài 2: useState và bài toán State Management",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/f_auto,q_auto/v1792081969/test_video_2.mp4",
                duration_seconds=360,
                order_index=2
            )
            
            lesson_3 = Lesson(
                course_id=course.id,
                title="Bài 3: So sánh useMemo và useCallback khác nhau gì?",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/f_auto,q_auto/v1792082183/test_video_3.mp4",
                duration_seconds=360,
                order_index=3
            )
            
            
            lesson_4 = Lesson(
                course_id=course.id,
                title="Bài 4: useRef() hook | Cách sử dụng useRef() hook",
                video_url="https://res.cloudinary.com/in0zcyvu/video/upload/f_auto,q_auto/v1792081963/test_video_4.mp4",
                duration_seconds=360,
                order_index=4
            )
            db.add_all([lesson_1, lesson_2, lesson_3, lesson_4])
            await db.flush()

            # 4. Giả lập Transcript của video có gắn timestamp (giây)
            mock_transcript = [
                TranscriptSegment(start=0, end=15, text="Chào mừng bạn đến với bài học về useEffect trong React."),
                TranscriptSegment(start=16, end=45, text="Khi làm việc với useEffect, một sai lầm phổ biến là quên hàm cleanup."),
                TranscriptSegment(start=46, end=90, text="Hàm cleanup rất quan trọng khi bạn subscribe vào websocket, addEventListener hoặc set timeout."),
                TranscriptSegment(start=91, end=140, text="Nếu không cleanup, khi component unmount, các listener cũ vẫn chạy ngầm gây ra hiện tượng memory leak."),
                TranscriptSegment(start=141, end=200, text="Cú pháp cleanup rất đơn giản: bạn chỉ cần return một function bên trong callback của useEffect."),
                TranscriptSegment(start=201, end=270, text="Đối với dependency array, nếu để rỗng mảng ngoặc vuông, effect chỉ chạy một lần sau mount."),
                TranscriptSegment(start=271, end=340, text="Đặc biệt lưu ý khi fetch data bằng useEffect: nên sử dụng AbortController trong cleanup function để hủy request nếu user rời trang.")
            ]

            print("🧠 Đang chunking transcript và tạo embeddings vào PostgreSQL...")
            chunks_count = await ingest_lesson_transcript(
                db=db,
                course_id=course.id,
                lesson_id=lesson_1.id,
                segments=mock_transcript
            )
            
            await db.close()

            print(f"✅ Hoàn tất! Đã lưu thành công:")
            print(f"   - Course ID: {course.id}")
            print(f"   - Số lượng chunk vector đã ingest: {chunks_count}")


if __name__ == "__main__":
    asyncio.run(create_seed_data())