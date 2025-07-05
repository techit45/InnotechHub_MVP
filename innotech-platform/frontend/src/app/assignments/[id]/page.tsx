'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient, Assignment, Submission } from '@/lib/api';

export default function AssignmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [assignment, setAssignment] = useState<Assignment & { submissions: Submission[] } | null>(null);
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
    } catch (error) {
      setError('ไม่สามารถโหลดข้อมูลงานได้');
      console.error('Error loading assignment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGradeSubmission = async (submissionId: number, score: number, feedback: string, status: string) => {
    try {
      await apiClient.updateSubmission(submissionId, { score, feedback, status });
      await loadAssignment(); // Reload to get updated data
      alert('ให้คะแนนสำเร็จ!');
    } catch (error) {
      alert('เกิดข้อผิดพลาดในการให้คะแนน');
      console.error('Error grading submission:', error);
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

  const userSubmission = user?.role === 'student' 
    ? assignment.submissions.find(s => s.student_id === user.id)
    : null;

  const isOverdue = assignment.due_date && new Date(assignment.due_date) < new Date();

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
      <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Assignment Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                {assignment.title}
              </h1>
              {assignment.is_required && (
                <span className="inline-block px-3 py-1 text-sm bg-red-100 text-red-800 rounded-full">
                  งานบังคับ
                </span>
              )}
            </div>
            
            {user?.role === 'student' && !userSubmission && !isOverdue && (
              <Link
                href={`/assignments/${assignment.id}/submit`}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
              >
                ส่งงาน
              </Link>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500 mb-1">คะแนนเต็ม</h3>
              <p className="text-2xl font-bold text-gray-900">{assignment.max_score}</p>
            </div>
            
            {assignment.due_date && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="text-sm font-medium text-gray-500 mb-1">กำหนดส่ง</h3>
                <p className={`text-lg font-semibold ${isOverdue ? 'text-red-600' : 'text-gray-900'}`}>
                  {new Date(assignment.due_date).toLocaleDateString('th-TH', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
                {isOverdue && (
                  <p className="text-sm text-red-600 mt-1">เลยกำหนดแล้ว</p>
                )}
              </div>
            )}
            
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500 mb-1">ผู้ส่งงาน</h3>
              <p className="text-2xl font-bold text-gray-900">{assignment.submissions?.length || 0}</p>
            </div>
          </div>

          {assignment.description && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">รายละเอียด</h3>
              <p className="text-gray-700 whitespace-pre-wrap">{assignment.description}</p>
            </div>
          )}

          {assignment.instructions && (
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">คำแนะนำการทำงาน</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-gray-700 whitespace-pre-wrap">{assignment.instructions}</p>
              </div>
            </div>
          )}
        </div>

        {/* Student Submission Status */}
        {user?.role === 'student' && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">สถานะการส่งงาน</h2>
            
            {userSubmission ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">สถานะ:</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                    userSubmission.status === 'submitted' ? 'bg-blue-100 text-blue-800' :
                    userSubmission.status === 'reviewed' ? 'bg-yellow-100 text-yellow-800' :
                    userSubmission.status === 'approved' ? 'bg-green-100 text-green-800' :
                    userSubmission.status === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {userSubmission.status === 'submitted' ? 'ส่งแล้ว' :
                     userSubmission.status === 'reviewed' ? 'ตรวจแล้ว' :
                     userSubmission.status === 'approved' ? 'ผ่าน' :
                     userSubmission.status === 'rejected' ? 'ไม่ผ่าน' :
                     'รอดำเนินการ'}
                  </span>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-gray-700">ส่งงานเมื่อ:</span>
                  <span className="text-gray-900">
                    {new Date(userSubmission.submitted_at).toLocaleDateString('th-TH', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </span>
                </div>

                {userSubmission.score !== null && userSubmission.score !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-gray-700">คะแนน:</span>
                    <span className="text-2xl font-bold text-blue-600">
                      {userSubmission.score}/{assignment.max_score}
                    </span>
                  </div>
                )}

                {userSubmission.feedback && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">ความคิดเห็นจากผู้สอน:</h4>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-gray-700">{userSubmission.feedback}</p>
                    </div>
                  </div>
                )}

                {userSubmission.file_url && (
                  <div>
                    <span className="text-gray-700">ไฟล์ที่ส่ง:</span>
                    <a
                      href={`http://localhost:8000${userSubmission.file_url}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-2 text-blue-600 hover:text-blue-500 underline"
                    >
                      {userSubmission.file_name || 'ดาวน์โหลดไฟล์'}
                    </a>
                  </div>
                )}

                {userSubmission.content && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">เนื้อหาที่ส่ง:</h4>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-gray-700 whitespace-pre-wrap">{userSubmission.content}</p>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">คุณยังไม่ได้ส่งงานนี้</p>
                {!isOverdue && (
                  <Link
                    href={`/assignments/${assignment.id}/submit`}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
                  >
                    ส่งงานตอนนี้
                  </Link>
                )}
                {isOverdue && (
                  <p className="text-red-600 text-sm">เลยกำหนดส่งแล้ว</p>
                )}
              </div>
            )}
          </div>
        )}

        {/* Submissions List for Trainers */}
        {(user?.role === 'trainer' || user?.role === 'admin') && assignment.submissions && assignment.submissions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">งานที่ส่งมา ({assignment.submissions.length})</h2>
            
            <div className="space-y-4">
              {assignment.submissions.map((submission) => (
                <div key={submission.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-medium text-gray-900">
                        {submission.student?.full_name || `นักเรียน ID: ${submission.student_id}`}
                      </h4>
                      <p className="text-sm text-gray-500">
                        ส่งเมื่อ: {new Date(submission.submitted_at).toLocaleDateString('th-TH')}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      submission.status === 'submitted' ? 'bg-blue-100 text-blue-800' :
                      submission.status === 'reviewed' ? 'bg-yellow-100 text-yellow-800' :
                      submission.status === 'approved' ? 'bg-green-100 text-green-800' :
                      submission.status === 'rejected' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {submission.status === 'submitted' ? 'ส่งแล้ว' :
                       submission.status === 'reviewed' ? 'ตรวจแล้ว' :
                       submission.status === 'approved' ? 'ผ่าน' :
                       submission.status === 'rejected' ? 'ไม่ผ่าน' :
                       'รอดำเนินการ'}
                    </span>
                  </div>

                  {submission.content && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-gray-700 mb-1">เนื้อหา:</h5>
                      <p className="text-gray-600 text-sm bg-gray-50 p-2 rounded">
                        {submission.content}
                      </p>
                    </div>
                  )}

                  {submission.file_url && (
                    <div className="mb-3">
                      <a
                        href={`http://localhost:8000${submission.file_url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-500 underline text-sm"
                      >
                        📎 {submission.file_name || 'ดาวน์โหลดไฟล์'}
                      </a>
                    </div>
                  )}

                  {submission.score !== null && submission.score !== undefined && (
                    <div className="mb-3">
                      <span className="text-sm text-gray-700">คะแนน: </span>
                      <span className="font-bold text-blue-600">
                        {submission.score}/{assignment.max_score}
                      </span>
                    </div>
                  )}

                  {submission.feedback && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-gray-700 mb-1">ความคิดเห็น:</h5>
                      <p className="text-gray-600 text-sm bg-yellow-50 p-2 rounded">
                        {submission.feedback}
                      </p>
                    </div>
                  )}

                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        const score = prompt('ใส่คะแนน (0-' + assignment.max_score + '):', submission.score?.toString() || '');
                        const feedback = prompt('ความคิดเห็น:', submission.feedback || '');
                        if (score !== null && feedback !== null) {
                          handleGradeSubmission(submission.id, parseInt(score), feedback, 'reviewed');
                        }
                      }}
                      className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                      ให้คะแนน
                    </button>
                    
                    <button
                      onClick={() => handleGradeSubmission(submission.id, submission.score || 0, submission.feedback || '', 'approved')}
                      className="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      ผ่าน
                    </button>
                    
                    <button
                      onClick={() => handleGradeSubmission(submission.id, submission.score || 0, submission.feedback || '', 'rejected')}
                      className="bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                    >
                      ไม่ผ่าน
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}