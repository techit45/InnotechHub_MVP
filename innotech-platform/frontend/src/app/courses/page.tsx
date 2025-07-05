'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Course } from '@/lib/api';

export default function CoursesPage() {
  const { user, isAuthenticated } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      setLoading(true);
      const coursesData = await apiClient.getCourses();
      setCourses(coursesData);
    } catch (error) {
      setError('ไม่สามารถโหลดหลักสูตรได้');
      console.error('Error loading courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (courseId: number) => {
    if (!isAuthenticated) {
      alert('กรุณาเข้าสู่ระบบก่อนลงทะเบียนเรียน');
      return;
    }

    try {
      await apiClient.enrollCourse(courseId);
      alert('ลงทะเบียนเรียนสำเร็จ!');
    } catch (error) {
      alert(error instanceof Error ? error.message : 'เกิดข้อผิดพลาดในการลงทะเบียน');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">กำลังโหลดหลักสูตร...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-semibold text-gray-900">
                Innotech Platform
              </Link>
            </div>
            
            <div className="flex items-center space-x-4">
              {isAuthenticated && user ? (
                <>
                  <Link
                    href="/dashboard"
                    className="text-gray-700 hover:text-gray-900"
                  >
                    แดชบอร์ด
                  </Link>
                  <span className="text-sm text-gray-700">
                    {user.full_name}
                  </span>
                </>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-gray-700 hover:text-gray-900"
                  >
                    เข้าสู่ระบบ
                  </Link>
                  <Link
                    href="/register"
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                  >
                    สมัครสมาชิก
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="bg-blue-600 text-white">
        <div className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl font-extrabold">
              คลังหลักสูตร
            </h1>
            <p className="mt-4 text-xl">
              เรียนรู้เทคโนโลยีและนวัตกรรมใหม่ๆ กับผู้เชี่ยวชาญ
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-8 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {courses.length === 0 ? (
          <div className="text-center py-16">
            <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ยังไม่มีหลักสูตร
            </h3>
            <p className="text-gray-500 mb-4">
              ขณะนี้ยังไม่มีหลักสูตรที่เผยแพร่ กรุณาติดตามใหม่ในภายหลัง
            </p>
            {user?.role === 'trainer' && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 inline-block">
                <p className="text-blue-800 text-sm">
                  <strong>สำหรับผู้สอน:</strong> คุณสามารถสร้างหลักสูตรใหม่ได้ผ่าน API
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div key={course.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                {/* Course Image */}
                <div className="h-48 bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center">
                  {course.thumbnail_url ? (
                    <img
                      src={course.thumbnail_url}
                      alt={course.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-white text-4xl font-bold">
                      {course.title.charAt(0)}
                    </div>
                  )}
                </div>

                {/* Course Content */}
                <div className="p-6">
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {course.title}
                  </h3>
                  
                  {course.short_description && (
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {course.short_description}
                    </p>
                  )}

                  <div className="flex items-center justify-between mb-4">
                    {course.is_free ? (
                      <span className="text-green-600 font-semibold">ฟรี</span>
                    ) : (
                      <span className="text-gray-900 font-semibold">
                        ฿{(course.price / 100).toLocaleString()}
                      </span>
                    )}
                    
                    {course.duration_hours && (
                      <span className="text-sm text-gray-500">
                        {course.duration_hours} ชั่วโมง
                      </span>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <Link
                      href={`/courses/${course.id}`}
                      className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                    >
                      ดูรายละเอียด
                    </Link>
                    
                    {isAuthenticated ? (
                      <button
                        onClick={() => handleEnroll(course.id)}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
                      >
                        ลงทะเบียน
                      </button>
                    ) : (
                      <Link
                        href="/login"
                        className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 text-sm"
                      >
                        เข้าสู่ระบบ
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}