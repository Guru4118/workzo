import apiClient from './client'

// Get paginated list of approved jobs
export const getJobs = async ({ page = 1, perPage = 20, q = '', source = '', location = '' }) => {
  const params = new URLSearchParams()
  params.append('page', page)
  params.append('per_page', perPage)
  if (q) params.append('q', q)
  if (source) params.append('source', source)
  if (location) params.append('location', location)

  const response = await apiClient.get(`/jobs?${params.toString()}`)
  return response.data
}

// Get single job by ID
export const getJobById = async (id) => {
  const response = await apiClient.get(`/jobs/${id}`)
  return response.data
}

// Get jobs by source
export const getJobsBySource = async (source, { page = 1, perPage = 20 }) => {
  const params = new URLSearchParams()
  params.append('page', page)
  params.append('per_page', perPage)

  const response = await apiClient.get(`/jobs/source/${source}?${params.toString()}`)
  return response.data
}
