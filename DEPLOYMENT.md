# 🚀 Deployment Instructions

## 📋 Prerequisites

1. **GitHub Account** - สำหรับ push repository
2. **Vercel Account** - สำหรับ deploy frontend (ฟรี)
3. **AWS Account** - สำหรับ backend และ database (free tier)

## 🎯 Step 1: Deploy Frontend to Vercel

### 1.1 Push to GitHub
```bash
# สร้าง repository ใหม่บน GitHub
# ชื่อ: innotech-platform-mvp

# Add remote และ push
git remote add origin https://github.com/YOUR_USERNAME/innotech-platform-mvp.git
git branch -M main
git push -u origin main
```

### 1.2 Deploy to Vercel
1. ไปที่ [vercel.com](https://vercel.com)
2. Sign in ด้วย GitHub
3. Click "New Project"
4. เลือก repository: `innotech-platform-mvp`
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `innotech-platform/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 1.3 Environment Variables
เพิ่ม environment variables ใน Vercel dashboard:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Innotech Platform
NEXT_PUBLIC_ENVIRONMENT=production
```

## 🔧 Step 2: Deploy Backend to AWS

### 2.1 Setup AWS Account
1. สมัคร AWS Free Tier
2. Create IAM user with appropriate permissions
3. Install AWS CLI และ configure credentials

### 2.2 Deploy Database (RDS PostgreSQL)
```bash
# สร้าง RDS instance ผ่าน AWS Console
# Instance class: db.t3.micro (free tier)
# Storage: 20GB (free tier)
# Engine: PostgreSQL 14
```

### 2.3 Deploy Backend (Lambda + API Gateway)
```bash
# Package application
cd innotech-platform/backend
pip install -r requirements.txt -t .
zip -r function.zip .

# Deploy via AWS CLI หรือ AWS Console
```

## 🔗 Environment Configuration

### Production URLs:
- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-api-id.execute-api.region.amazonaws.com`
- Database: RDS endpoint

### Update Environment Variables:
1. Vercel: อัปเดต `NEXT_PUBLIC_API_URL`
2. AWS Lambda: อัปเดต `DATABASE_URL`
3. Backend CORS: เพิ่ม Vercel domain

## ✅ Testing Checklist

### Frontend (Vercel):
- [ ] หน้า home โหลดได้
- [ ] Authentication ทำงาน
- [ ] API calls ไปที่ backend สำเร็จ

### Backend (AWS):
- [ ] API endpoints respond ได้
- [ ] Database connection ทำงาน
- [ ] Authentication tokens valid

### Integration:
- [ ] ลงทะเบียนผู้ใช้ใหม่ได้
- [ ] เข้าสู่ระบบได้
- [ ] สร้างและดูหลักสูตรได้
- [ ] ส่งงานได้ (ถ้า S3 setup แล้ว)

## 💰 Cost Monitoring

### Free Tier Limits:
- **Vercel**: Unlimited static hosting
- **AWS Lambda**: 1M requests/month
- **RDS**: 750 hours/month (12 months)
- **S3**: 5GB storage

### Estimated Monthly Cost:
- **Year 1**: $0-5/month (free tier)
- **After free tier**: $20-50/month

## 🔧 Troubleshooting

### Common Issues:
1. **CORS errors**: Check allowed origins in backend
2. **Environment variables**: Verify all URLs are correct
3. **Build errors**: Check next.config.ts configuration
4. **Database connection**: Verify security groups and credentials

### Debug Commands:
```bash
# Check Vercel logs
vercel logs

# Check AWS Lambda logs
aws logs describe-log-groups

# Test API directly
curl https://your-api-url.execute-api.region.amazonaws.com/health
```