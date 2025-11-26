import { useState } from 'react'
import {
  HiOutlineCheck,
  HiOutlineX,
  HiOutlineExternalLink,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
} from 'react-icons/hi'
import {
  usePendingJobs,
  useApproveJob,
  useRejectJob,
  useBulkApprove,
  useBulkReject,
} from '../hooks/useJobs'

const PAGE_SIZE = 20

const PendingJobsPage = () => {
  const [page, setPage] = useState(1)
  const [selectedJobs, setSelectedJobs] = useState([])

  const { data, isLoading, error } = usePendingJobs({
    page,
    per_page: PAGE_SIZE,
  })

  const approveJob = useApproveJob()
  const rejectJob = useRejectJob()
  const bulkApprove = useBulkApprove()
  const bulkReject = useBulkReject()

  const jobs = data?.data || []
  const total = data?.total || 0
  const totalPages = data?.total_pages || Math.ceil(total / PAGE_SIZE)

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedJobs(jobs.map((job) => job.id))
    } else {
      setSelectedJobs([])
    }
  }

  const handleSelectJob = (jobId) => {
    setSelectedJobs((prev) =>
      prev.includes(jobId)
        ? prev.filter((id) => id !== jobId)
        : [...prev, jobId]
    )
  }

  const handleApprove = async (jobId) => {
    await approveJob.mutateAsync(jobId)
    setSelectedJobs((prev) => prev.filter((id) => id !== jobId))
  }

  const handleReject = async (jobId) => {
    await rejectJob.mutateAsync({ id: jobId, reason: 'Rejected by admin' })
    setSelectedJobs((prev) => prev.filter((id) => id !== jobId))
  }

  const handleBulkApprove = async () => {
    await bulkApprove.mutateAsync(selectedJobs)
    setSelectedJobs([])
  }

  const handleBulkReject = async () => {
    await bulkReject.mutateAsync({ jobIds: selectedJobs, reason: 'Bulk rejected by admin' })
    setSelectedJobs([])
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    })
  }

  if (error) {
    return (
      <div className="card p-6 text-center">
        <p className="text-red-600">Error loading jobs: {error.message}</p>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Pending Jobs</h2>
          <p className="text-gray-500 mt-1">{total} jobs awaiting review</p>
        </div>

        {/* Bulk Actions */}
        {selectedJobs.length > 0 && (
          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">
              {selectedJobs.length} selected
            </span>
            <button
              onClick={handleBulkApprove}
              disabled={bulkApprove.isPending}
              className="btn-success text-sm"
            >
              <HiOutlineCheck className="h-4 w-4 mr-1" />
              Approve All
            </button>
            <button
              onClick={handleBulkReject}
              disabled={bulkReject.isPending}
              className="btn-danger text-sm"
            >
              <HiOutlineX className="h-4 w-4 mr-1" />
              Reject All
            </button>
          </div>
        )}
      </div>

      {/* Jobs Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading...</div>
        ) : jobs.length === 0 ? (
          <div className="p-8 text-center text-gray-500">
            No pending jobs to review
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th className="w-12">
                      <input
                        type="checkbox"
                        checked={
                          selectedJobs.length === jobs.length && jobs.length > 0
                        }
                        onChange={handleSelectAll}
                        className="rounded"
                      />
                    </th>
                    <th>Job</th>
                    <th>Company</th>
                    <th>Source</th>
                    <th>Date</th>
                    <th className="w-32">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.id}>
                      <td>
                        <input
                          type="checkbox"
                          checked={selectedJobs.includes(job.id)}
                          onChange={() => handleSelectJob(job.id)}
                          className="rounded"
                        />
                      </td>
                      <td>
                        <div className="max-w-xs">
                          <p className="font-medium text-gray-900 truncate">
                            {job.title}
                          </p>
                          {job.url && (
                            <a
                              href={job.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-primary-600 hover:text-primary-700 text-xs flex items-center gap-1"
                            >
                              View Original
                              <HiOutlineExternalLink className="h-3 w-3" />
                            </a>
                          )}
                        </div>
                      </td>
                      <td className="text-gray-600">{job.company}</td>
                      <td>
                        <span className="px-2 py-1 bg-gray-100 rounded-full text-xs capitalize">
                          {job.source}
                        </span>
                      </td>
                      <td className="text-gray-500 text-sm">
                        {formatDate(job.scraped_at)}
                      </td>
                      <td>
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleApprove(job.id)}
                            disabled={approveJob.isPending}
                            className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Approve"
                          >
                            <HiOutlineCheck className="h-5 w-5" />
                          </button>
                          <button
                            onClick={() => handleReject(job.id)}
                            disabled={rejectJob.isPending}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Reject"
                          >
                            <HiOutlineX className="h-5 w-5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="px-6 py-4 border-t border-gray-100 flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Showing {(page - 1) * PAGE_SIZE + 1} to{' '}
                  {Math.min(page * PAGE_SIZE, total)} of {total}
                </p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <HiOutlineChevronLeft className="h-5 w-5" />
                  </button>
                  <span className="text-sm text-gray-600">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <HiOutlineChevronRight className="h-5 w-5" />
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default PendingJobsPage
