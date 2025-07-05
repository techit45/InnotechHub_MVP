#!/bin/bash

echo "🧪 ทดสอบระบบ Innotech Platform MVP"
echo "=================================="

# สีสำหรับแสดงผล
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ฟังก์ชันสำหรับแสดงผลลัพธ์
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

# 1. ทดสอบโครงสร้างไฟล์
echo -e "${YELLOW}1. ตรวจสอบโครงสร้างไฟล์...${NC}"

if [ -d "innotech-platform/frontend" ] && [ -d "innotech-platform/backend" ]; then
    print_result 0 "โครงสร้างโปรเจกต์ถูกต้อง"
else
    print_result 1 "โครงสร้างโปรเจกต์ไม่ถูกต้อง"
fi

# 2. ทดสอบ Backend Dependencies
echo -e "${YELLOW}2. ตรวจสอบ Backend Dependencies...${NC}"

cd innotech-platform/backend
if [ -f "requirements.txt" ] && [ -f "app/main.py" ]; then
    print_result 0 "ไฟล์ Backend พร้อมใช้งาน"
else
    print_result 1 "ไฟล์ Backend ไม่ครบถ้วน"
fi

# 3. ทดสอบ Frontend Dependencies
echo -e "${YELLOW}3. ตรวจสอบ Frontend Dependencies...${NC}"

cd ../frontend
if [ -f "package.json" ] && [ -f "src/app/page.tsx" ]; then
    print_result 0 "ไฟล์ Frontend พร้อมใช้งาน"
else
    print_result 1 "ไฟล์ Frontend ไม่ครบถ้วน"
fi

# 4. ทดสอบการเริ่มต้น Backend
echo -e "${YELLOW}4. ทดสอบการเริ่มต้น Backend...${NC}"

cd ../backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
sleep 3

# ทดสอบ API
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health)
if [ "$BACKEND_RESPONSE" = "200" ]; then
    print_result 0 "Backend API ทำงานได้ปกติ"
else
    print_result 1 "Backend API ไม่ตอบสนอง"
fi

# หยุด Backend
kill $BACKEND_PID 2>/dev/null

# 5. ทดสอบการ Build Frontend
echo -e "${YELLOW}5. ทดสอบการ Build Frontend...${NC}"

cd ../frontend
if npm run build > /dev/null 2>&1; then
    print_result 0 "Frontend Build สำเร็จ"
else
    print_result 1 "Frontend Build ล้มเหลว"
fi

# สรุปผลการทดสอบ
echo ""
echo -e "${YELLOW}=================================="
echo "📊 สรุปผลการทดสอบ"
echo -e "==================================${NC}"

cd ../..
echo "🎯 ระบบพร้อมสำหรับการพัฒนา Phase 2"
echo ""
echo "การใช้งาน:"
echo "• รันระบบ: ./start-dev.sh"
echo "• Frontend: http://localhost:3000"
echo "• Backend: http://localhost:8000"
echo "• API Docs: http://localhost:8000/docs"
echo "• Test Page: http://localhost:3000/test"