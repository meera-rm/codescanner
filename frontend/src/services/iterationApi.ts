/**
 * Iteration API Service
 * Handles all API calls for iteration until clean feature
 */

export interface IterationStep {
  iteration_number: number;
  grade_before: string;
  grade_after: string;
  issues_fixed: number;
  agent_selected: string;
  fix_description: string;
  validation_passed: boolean;
  applied_at?: string;
  changes?: Record<string, any>;
}

export interface IterationJobStatus {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';
  start_grade: string;
  final_grade: string;
  grade_improvement: number;
  iterations_count: number;
  max_iterations: number;
  current_iteration: number;
  target_grade: string;
  progress_percent: number;
  history: IterationStep[];
  metrics: Record<string, any>;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface IterationProgress {
  job_id: string;
  status: string;
  current_grade: string;
  progress_percent: number;
  iterations_count: number;
  max_iterations: number;
}

class IterationApiService {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api/v1/iteration') {
    this.baseUrl = baseUrl;
  }

  /**
   * Start a new iteration job
   */
  async startJob(params: {
    directory_path: string;
    target_grade?: string;
    max_iterations?: number;
  }): Promise<{ job_id: string; status: string; message: string; created_at: string }> {
    const response = await fetch(`${this.baseUrl}/fix-until-clean`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Failed to start job: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get full job status with history
   */
  async getJobStatus(jobId: string): Promise<IterationJobStatus> {
    const response = await fetch(`${this.baseUrl}/${jobId}`);

    if (!response.ok) {
      throw new Error(`Failed to get job status: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get lightweight progress update (no history)
   */
  async getJobProgress(jobId: string): Promise<IterationProgress> {
    const response = await fetch(`${this.baseUrl}/${jobId}/progress`);

    if (!response.ok) {
      throw new Error(`Failed to get job progress: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Get iteration history only
   */
  async getJobHistory(jobId: string): Promise<IterationStep[]> {
    const response = await fetch(`${this.baseUrl}/${jobId}/history`);

    if (!response.ok) {
      throw new Error(`Failed to get job history: ${response.statusText}`);
    }

    const data = await response.json();
    return data.history || [];
  }

  /**
   * Cancel a running job
   */
  async cancelJob(jobId: string, reason?: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/${jobId}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reason }),
    });

    if (!response.ok) {
      throw new Error(`Failed to cancel job: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Delete a job and its history
   */
  async deleteJob(jobId: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/${jobId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`Failed to delete job: ${response.statusText}`);
    }

    return response.json();
  }
}

export const iterationApi = new IterationApiService();
