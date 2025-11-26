import { useQuery } from '@tanstack/react-query'
import { getJobs, getJobById, getJobsBySource } from '../api/jobs'

// Hook for fetching paginated jobs
export const useJobs = (params = {}) => {
  return useQuery({
    queryKey: ['jobs', params],
    queryFn: () => getJobs(params),
    keepPreviousData: true,
  })
}

// Hook for fetching single job
export const useJob = (id) => {
  return useQuery({
    queryKey: ['job', id],
    queryFn: () => getJobById(id),
    enabled: !!id,
  })
}

// Hook for fetching jobs by source
export const useJobsBySource = (source, params = {}) => {
  return useQuery({
    queryKey: ['jobs', 'source', source, params],
    queryFn: () => getJobsBySource(source, params),
    enabled: !!source,
    keepPreviousData: true,
  })
}
