import apiClient from './client'

export const jobsApi = {
  // Public endpoints
  getJobs: async (params = {}) => {
    const response = await apiClient.get('/jobs', { params })
    return response.data
  },

  getJob: async (id) => {
    const response = await apiClient.get(`/jobs/${id}`)
    return response.data
  },

  // Admin endpoints
  getAdminStats: async () => {
    const response = await apiClient.get('/admin/stats')
    return response.data
  },

  getPendingJobs: async (params = {}) => {
    const response = await apiClient.get('/admin/pending', { params })
    return response.data
  },

  approveJob: async (id) => {
    const response = await apiClient.post('/admin/approve', { job_id: id })
    return response.data
  },

  rejectJob: async (id, reason = 'Rejected by admin') => {
    const response = await apiClient.post('/admin/reject', { job_id: id, reason })
    return response.data
  },

  bulkApprove: async (jobIds) => {
    const response = await apiClient.post('/admin/bulk-approve', {
      job_ids: jobIds,
    })
    return response.data
  },

  bulkReject: async (jobIds, reason = 'Bulk rejected by admin') => {
    const response = await apiClient.post('/admin/bulk-reject', {
      job_ids: jobIds,
      reason,
    })
    return response.data
  },
}

export default jobsApi
