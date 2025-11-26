import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import jobsApi from '../api/jobs'

export const useAdminStats = () => {
  return useQuery({
    queryKey: ['adminStats'],
    queryFn: jobsApi.getAdminStats,
    staleTime: 30000, // 30 seconds
  })
}

export const usePendingJobs = (params = {}) => {
  return useQuery({
    queryKey: ['pendingJobs', params],
    queryFn: () => jobsApi.getPendingJobs(params),
  })
}

export const useApproveJob = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: jobsApi.approveJob,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingJobs'] })
      queryClient.invalidateQueries({ queryKey: ['adminStats'] })
    },
  })
}

export const useRejectJob = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, reason }) => jobsApi.rejectJob(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingJobs'] })
      queryClient.invalidateQueries({ queryKey: ['adminStats'] })
    },
  })
}

export const useBulkApprove = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: jobsApi.bulkApprove,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingJobs'] })
      queryClient.invalidateQueries({ queryKey: ['adminStats'] })
    },
  })
}

export const useBulkReject = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ jobIds, reason }) => jobsApi.bulkReject(jobIds, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pendingJobs'] })
      queryClient.invalidateQueries({ queryKey: ['adminStats'] })
    },
  })
}
