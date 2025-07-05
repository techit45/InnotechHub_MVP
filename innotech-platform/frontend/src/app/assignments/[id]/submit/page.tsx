'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Assignment } from '@/lib/api';

export default function SubmitAssignmentPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [content, setContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const assignmentId = parseInt(params.id as string);

  useEffect(() => {
    if (isAuthenticated && assignmentId) {
      loadAssignment();
    }
  }, [isAuthenticated, assignmentId]);

  const loadAssignment = async () => {
    try {
      setLoading(true);
      const assignmentData = await apiClient.getAssignment(assignmentId);
      setAssignment(assignmentData);
      
      // ตรวจสอบว่าส่งงานแล้วหรือยัง
      const userSubmission = assignmentData.submissions?.find(s => s.student_id === user?.id);
      if (userSubmission) {
        router.push(`/assignments/${assignmentId}`);
        return;
      }
    } catch (error) {
      setError('ไม่สามารถโหลดข้อมูลงานได้');
      console.error('Error loading assignment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // ตรวจสอบขนาดไฟล์ (10MB)
      if (file.size > 10 * 1024 * 1024) {
        alert('ไฟล์มีขนาดใหญ่เกินไป (สูงสุด 10MB)');
        return;
      }
      
      // ตรวจสอบประเภทไฟล์
      const allowedTypes = ['.pdf', '.doc', '.docx', '.txt', '.zip', '.jpg', '.jpeg', '.png', '.gif'];
      const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!allowedTypes.includes(fileExt)) {
        alert('ประเภทไฟล์ไม่ได้รับอนุญาต\nอนุญาต: ' + allowedTypes.join(', '));
        return;
      }
      
      setSelectedFile(file);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim() && !selectedFile) {
      alert('กรุณากรอกเนื้อหาหรือเลือกไฟล์');
      return;
    }

    if (!assignment) return;

    setSubmitting(true);
    
    try {
      await apiClient.submitAssignment(
        assignmentId,
        content.trim() || undefined,
        selectedFile || undefined
      );
      
      alert('ส่งงานสำเร็จ!');
      router.push(`/assignments/${assignmentId}`);
    } catch (error) {
      alert(error instanceof Error ? error.message : 'เกิดข้อผิดพลาดในการส่งงาน');
      console.error('Error submitting assignment:', error);
    } finally {
      setSubmitting(false);
    }
  };

  if (!isAuthenticated || user?.role !== 'student') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">ไม่มีสิทธิ์เข้าถึง</h2>
          <p className="text-gray-600 mb-4">เฉพาะนักเรียนเท่านั้นที่สามารถส่งงานได้</p>
          <Link
            href="/assignments"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            กลับหน้ารายการงาน
          </Link>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">กำลังโหลดข้อมูลงาน...</div>
      </div>
    );
  }

  if (error || !assignment) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">ไม่พบข้อมูลงาน</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Link
            href="/assignments"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            กลับหน้ารายการงาน
          </Link>
        </div>
      </div>
    );
  }

  const isOverdue = assignment.due_date && new Date(assignment.due_date) < new Date();

  if (isOverdue) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">เลยกำหนดส่งแล้ว</h2>
          <p className="text-gray-600 mb-4">งานนี้เลยกำหนดส่งเมื่อ {assignment.due_date ? new Date(assignment.due_date).toLocaleDateString('th-TH') : 'ไม่ระบุ'}</p>
          <Link
            href={`/assignments/${assignmentId}`}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            กลับหน้างาน
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link href="/" className="text-xl font-semibold text-gray-900">
                Innotech Platform
              </Link>
              <span className="text-gray-500">/</span>
              <Link href="/assignments" className="text-blue-600 hover:text-blue-500">
                งานที่มอบหมาย
              </Link>
              <span className="text-gray-500">/</span>
              <Link href={`/assignments/${assignmentId}`} className="text-blue-600 hover:text-blue-500">
                {assignment.title}
              </Link>
              <span className="text-gray-500">/</span>
              <span className="text-gray-700">ส่งงาน</span>
            </div>
            
            <div className="flex items-center space-x-4">
              {user && (
                <span className="text-sm text-gray-700">
                  {user.full_name}
                </span>
              )}
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-3xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Assignment Info */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">{assignment.title}</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <span className="text-sm text-gray-500">คะแนนเต็ม:</span>
              <span className="ml-2 font-semibold">{assignment.max_score} คะแนน</span>
            </div>
            
            {assignment.due_date && (
              <div>
                <span className="text-sm text-gray-500">กำหนดส่ง:</span>
                <span className="ml-2 font-semibold">
                  {new Date(assignment.due_date).toLocaleDateString('th-TH', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
            )}
          </div>

          {assignment.description && (
            <div className="mb-4">
              <h3 className="text-sm font-medium text-gray-700 mb-2">รายละเอียด:</h3>
              <p className="text-gray-600 whitespace-pre-wrap">{assignment.description}</p>
            </div>
          )}

          {assignment.instructions && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-2">คำแนะนำ:</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <p className="text-gray-700 whitespace-pre-wrap">{assignment.instructions}</p>
              </div>
            </div>
          )}
        </div>

        {/* Submit Form */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">ส่งงาน</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Text Content */}
            <div>
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                เนื้อหางาน (ไม่บังคับ)
              </label>
              <textarea
                id="content"
                value={content}
                onChange={(e) => setContent(e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="กรอกเนื้อหางานที่นี่..."
              />
            </div>

            {/* File Upload */}
            <div>
              <label htmlFor="file" className="block text-sm font-medium text-gray-700 mb-2">
                แนบไฟล์ (ไม่บังคับ)
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                <input
                  type="file"
                  id="file"
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".pdf,.doc,.docx,.txt,.zip,.jpg,.jpeg,.png,.gif"
                />
                <label
                  htmlFor="file"
                  className="cursor-pointer flex flex-col items-center"
                >
                  <svg className="w-12 h-12 text-gray-400 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <span className="text-sm text-gray-600">
                    {selectedFile ? selectedFile.name : 'คลิกเพื่อเลือกไฟล์ หรือลากไฟล์มาวางที่นี่'}
                  </span>
                  <span className="text-xs text-gray-500 mt-1">
                    รองรับ: PDF, DOC, DOCX, TXT, ZIP, JPG, PNG, GIF (สูงสุด 10MB)
                  </span>
                </label>
              </div>
              
              {selectedFile && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-green-800">
                      ✓ เลือกไฟล์: {selectedFile.name} ({(selectedFile.size / (1024*1024)).toFixed(2)} MB)
                    </span>
                    <button
                      type="button"
                      onClick={() => setSelectedFile(null)}
                      className="text-green-600 hover:text-green-500"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Notice */}
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex">
                <svg className="w-5 h-5 text-yellow-400 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="text-sm font-medium text-yellow-800">ข้อควรระวัง</h4>
                  <p className="text-sm text-yellow-700 mt-1">
                    กรุณาตรวจสอบงานให้เรียบร้อยก่อนส่ง เมื่อส่งแล้วจะไม่สามารถแก้ไขได้
                  </p>
                </div>
              </div>
            </div>

            {/* Submit Buttons */}
            <div className="flex justify-between">
              <Link
                href={`/assignments/${assignmentId}`}
                className="bg-gray-500 text-white px-6 py-3 rounded-lg hover:bg-gray-600"
              >
                ยกเลิก
              </Link>
              
              <button
                type="submit"
                disabled={submitting || (!content.trim() && !selectedFile)}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submitting ? 'กำลังส่งงาน...' : 'ส่งงาน'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}