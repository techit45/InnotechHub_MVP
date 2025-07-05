#!/bin/bash

echo "🚀 เริ่มต้นระบบ Innotech Platform MVP"
echo "====================================="

# ตรวจสอบพอร์ตที่ใช้งาน
echo "ตรวจสอบพอร์ตที่ใช้งาน..."
if lsof -ti:8000 > /dev/null; then
    echo "หยุดเซิร์ฟเวอร์ Backend ที่กำลังทำงานอยู่..."
    lsof -ti:8000 | xargs kill -9
fi

if lsof -ti:3000 > /dev/null; then
    echo "หยุดเซิร์ฟเวอร์ Frontend ที่กำลังทำงานอยู่..."
    lsof -ti:3000 | xargs kill -9
fi

# เริ่มต้น Backend
echo "เริ่มต้น Backend (FastAPI)..."
cd innotech-platform/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# รอให้ Backend เริ่มต้น
sleep 3

# เริ่มต้น Frontend
echo "เริ่มต้น Frontend (Next.js)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "✅ ระบบเริ่มต้นสำเร็จ!"
echo "====================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🧪 Test Page: http://localhost:3000/test"
echo ""
echo "กด Ctrl+C เพื่อหยุดการทำงาน"

# ฟังก์ชันสำหรับหยุดเซิร์ฟเวอร์
cleanup() {
    echo ""
    echo "หยุดการทำงานของระบบ..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ หยุดระบบเรียบร้อยแล้ว"
    exit 0
}

# ตั้งค่า trap สำหรับ Ctrl+C
trap cleanup SIGINT

# รอให้ผู้ใช้กด Ctrl+C
wait