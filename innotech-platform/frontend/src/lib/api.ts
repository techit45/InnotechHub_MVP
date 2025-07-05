const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'student' | 'trainer' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  full_name: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role?: 'student' | 'trainer' | 'admin';
}

export interface Course {
  id: number;
  title: string;
  description?: string;
  short_description?: string;
  thumbnail_url?: string;
  instructor_id: number;
  status: 'draft' | 'published' | 'archived';
  duration_hours?: number;
  price: number;
  is_free: boolean;
  created_at: string;
  modules: Module[];
}

export interface Module {
  id: number;
  course_id: number;
  title: string;
  description?: string;
  content?: string;
  video_url?: string;
  order_index: number;
  duration_minutes?: number;
  is_published: boolean;
  created_at: string;
}

export interface Assignment {
  id: number;
  course_id: number;
  title: string;
  description?: string;
  instructions?: string;
  max_score: number;
  due_date?: string;
  is_required: boolean;
  created_at: string;
  updated_at?: string;
  submissions_count?: number;
}

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  file_url?: string;
  file_name?: string;
  content?: string;
  status: 'pending' | 'submitted' | 'reviewed' | 'approved' | 'rejected';
  score?: number;
  feedback?: string;
  submitted_at: string;
  reviewed_at?: string;
  student?: User;
  assignment?: Assignment;
}

export interface AssignmentCreate {
  course_id: number;
  title: string;
  description?: string;
  instructions?: string;
  max_score?: number;
  due_date?: string;
  is_required?: boolean;
}

export interface SubmissionCreate {
  assignment_id: number;
  content?: string;
}

class APIClient {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    
    // ดึง token จาก localStorage (ถ้ามี)
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getHeaders(),
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Authentication methods
  async register(data: RegisterData): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: LoginData): Promise<{ access_token: string; token_type: string }> {
    const response = await this.request<{ access_token: string; token_type: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });

    // เก็บ token ใน localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', response.access_token);
      this.token = response.access_token;
    }

    return response;
  }

  async logout(): Promise<void> {
    await this.request('/auth/logout', {
      method: 'POST',
    });

    // ลบ token จาก localStorage
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      this.token = null;
    }
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Course methods
  async getCourses(skip: number = 0, limit: number = 100): Promise<Course[]> {
    return this.request<Course[]>(`/courses/?skip=${skip}&limit=${limit}`);
  }

  async getCourse(courseId: number): Promise<Course> {
    return this.request<Course>(`/courses/${courseId}`);
  }

  async enrollCourse(courseId: number): Promise<any> {
    return this.request(`/courses/${courseId}/enroll`, {
      method: 'POST',
    });
  }

  async getMyEnrollments(): Promise<any[]> {
    return this.request<any[]>('/courses/my/enrollments');
  }

  // Assignment methods
  async getAssignments(courseId?: number): Promise<Assignment[]> {
    const params = courseId ? `?course_id=${courseId}` : '';
    return this.request<Assignment[]>(`/assignments/${params}`);
  }

  async getAssignment(assignmentId: number): Promise<Assignment & { submissions: Submission[] }> {
    return this.request<Assignment & { submissions: Submission[] }>(`/assignments/${assignmentId}`);
  }

  async createAssignment(data: AssignmentCreate): Promise<Assignment> {
    return this.request<Assignment>('/assignments/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateAssignment(assignmentId: number, data: Partial<AssignmentCreate>): Promise<Assignment> {
    return this.request<Assignment>(`/assignments/${assignmentId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deleteAssignment(assignmentId: number): Promise<void> {
    return this.request(`/assignments/${assignmentId}`, {
      method: 'DELETE',
    });
  }

  // Submission methods
  async getSubmissions(assignmentId: number): Promise<Submission[]> {
    return this.request<Submission[]>(`/assignments/${assignmentId}/submissions`);
  }

  async submitAssignment(assignmentId: number, content?: string, file?: File): Promise<Submission> {
    const formData = new FormData();
    formData.append('assignment_id', assignmentId.toString());
    
    if (content) {
      formData.append('content', content);
    }
    
    if (file) {
      formData.append('file', file);
    }

    const response = await fetch(`${this.baseURL}/assignments/${assignmentId}/submissions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  async updateSubmission(submissionId: number, data: { 
    content?: string; 
    status?: string; 
    score?: number; 
    feedback?: string; 
  }): Promise<Submission> {
    return this.request<Submission>(`/assignments/submissions/${submissionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async getSubmission(submissionId: number): Promise<Submission> {
    return this.request<Submission>(`/assignments/submissions/${submissionId}`);
  }

  // ตรวจสอบว่า user login แล้วหรือไม่
  isAuthenticated(): boolean {
    return this.token !== null;
  }

  // ลบ authentication
  clearAuth(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      this.token = null;
    }
  }
}

export const apiClient = new APIClient();