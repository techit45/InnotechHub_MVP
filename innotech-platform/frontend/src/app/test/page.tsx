'use client';

import { useState, useEffect } from 'react';

export default function TestPage() {
  const [backendStatus, setBackendStatus] = useState<string>('กำลังตรวจสอบ...');
  const [apiData, setApiData] = useState<{ health: { status: string }; root: { message: string } } | null>(null);

  useEffect(() => {
    // ทดสอบการเชื่อมต่อ Backend
    const testBackendConnection = async () => {
      try {
        // ทดสอบ health check
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const healthResponse = await fetch(`${apiUrl}/health`);
        const healthData = await healthResponse.json();
        
        // ทดสอบ root endpoint
        const rootResponse = await fetch(`${apiUrl}/`);
        const rootData = await rootResponse.json();

        if (healthData.status === 'healthy') {
          setBackendStatus('✅ เชื่อมต่อ Backend สำเร็จ');
          setApiData({ health: healthData, root: rootData });
        } else {
          setBackendStatus('❌ Backend ไม่ตอบสนอง');
        }
      } catch (error) {
        setBackendStatus('❌ ไม่สามารถเชื่อมต่อ Backend ได้');
        console.error('Backend connection error:', error);
      }
    };

    testBackendConnection();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 text-center">
          ทดสอบระบบ MVP
        </h1>
        
        <div className="space-y-4">
          <div className="border rounded-lg p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">
              Frontend (Next.js)
            </h2>
            <p className="text-green-600">✅ ทำงานได้ปกติ</p>
            <p className="text-sm text-gray-600">
              URL: http://localhost:3001
            </p>
          </div>

          <div className="border rounded-lg p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">
              Backend (FastAPI)
            </h2>
            <p className={
              backendStatus.includes('✅') 
                ? 'text-green-600' 
                : 'text-red-600'
            }>
              {backendStatus}
            </p>
            <p className="text-sm text-gray-600">
              URL: {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
            </p>
          </div>

          {apiData && (
            <div className="border rounded-lg p-4">
              <h2 className="text-lg font-semibold text-gray-800 mb-2">
                ข้อมูลจาก API
              </h2>
              <div className="bg-gray-100 rounded p-3 text-sm">
                <p><strong>Health:</strong> {JSON.stringify(apiData.health)}</p>
                <p><strong>Root:</strong> {JSON.stringify(apiData.root)}</p>
              </div>
            </div>
          )}

          <div className="border rounded-lg p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-2">
              ระบบที่ติดตั้งแล้ว
            </h2>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>✅ Next.js 15 + TypeScript</li>
              <li>✅ Tailwind CSS</li>
              <li>✅ FastAPI + SQLAlchemy</li>
              <li>✅ SQLite Database</li>
              <li>✅ CORS Configuration</li>
            </ul>
          </div>

          <div className="text-center">
            <a
              href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              เปิด API Documentation
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}