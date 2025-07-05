'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Assignment } from '@/lib/api';

export default function AssignmentsPage() {
  const { user, isAuthenticated } = useAuth();
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) {
      loadAssignments();
    }
  }, [isAuthenticated]);

  const loadAssignments = async () => {
    try {
      setLoading(true);
      const assignmentsData = await apiClient.getAssignments();
      setAssignments(assignmentsData);
    } catch (error) {
      setError('ไม่สามารถโหลดรายการงานได้');
      console.error('Error loading assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">กรุณาเข้าสู่ระบบ</h2>
          <Link
            href="/login"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            เข้าสู่ระบบ
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">กำลังโหลดงานที่มอบหมาย...</div>
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
              <Link
                href="/courses"
                className="text-gray-700 hover:text-gray-900"
              >
                หลักสูตร
              </Link>
              <Link
                href="/dashboard"
                className="text-gray-700 hover:text-gray-900"
              >
                แดชบอร์ด
              </Link>
              {user && (
                <span className="text-sm text-gray-700">
                  {user.full_name}
                </span>
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
              งานที่มอบหมาย
            </h1>
            <p className="mt-4 text-xl">
              ดูงานที่ได้รับมอบหมายและส่งงานของคุณ
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

        {assignments.length === 0 ? (
          <div className="text-center py-16">
            <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              ยังไม่มีงานที่มอบหมาย
            </h3>
            <p className="text-gray-500 mb-4">
              ขณะนี้ยังไม่มีงานที่ได้รับมอบหมาย
            </p>
            <Link
              href="/courses"
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
              ไปดูหลักสูตร
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {assignments.map((assignment) => (
              <div key={assignment.id} className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xl font-semibold text-gray-900">
                      {assignment.title}
                    </h3>
                    {assignment.is_required && (
                      <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                        จำเป็น
                      </span>
                    )}
                  </div>
                  
                  {assignment.description && (
                    <p className="text-gray-600 mb-4 line-clamp-3">
                      {assignment.description}
                    </p>
                  )}

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-500">คะแนนเต็ม:</span>
                      <span className="font-medium">{assignment.max_score} คะแนน</span>
                    </div>
                    
                    {assignment.due_date && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">กำหนดส่ง:</span>
                        <span className="font-medium">
                          {new Date(assignment.due_date).toLocaleDateString('th-TH')}
                        </span>
                      </div>
                    )}

                    {assignment.submissions_count !== undefined && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-500">ส่งงานแล้ว:</span>
                        <span className="font-medium">{assignment.submissions_count} คน</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-between">
                    <Link
                      href={`/assignments/${assignment.id}`}
                      className="text-blue-600 hover:text-blue-500 text-sm font-medium"
                    >
                      ดูรายละเอียด
                    </Link>
                    
                    {user?.role === 'student' && (
                      <Link
                        href={`/assignments/${assignment.id}/submit`}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
                      >
                        ส่งงาน
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