import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { JobSearch, JobList, JobFilters } from '../components/jobs'
import Pagination from '../components/ui/Pagination'
import { useJobs } from '../hooks/useJobs'
import { DEFAULT_PAGE_SIZE } from '../utils/constants'

const JobsPage = () => {
  const [searchParams, setSearchParams] = useSearchParams()

  // Initialize state from URL params
  const [filters, setFilters] = useState({
    source: searchParams.get('source') || null,
    location: searchParams.get('location') || null,
  })
  const [search, setSearch] = useState(searchParams.get('search') || '')
  const [page, setPage] = useState(parseInt(searchParams.get('page')) || 1)

  // Build query params for API
  const queryParams = {
    page,
    perPage: DEFAULT_PAGE_SIZE,
    ...(search && { q: search }),
    ...(filters.source && { source: filters.source }),
    ...(filters.location && { location: filters.location }),
  }

  const { data, isLoading, error } = useJobs(queryParams)

  // Update URL when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (search) params.set('search', search)
    if (filters.source) params.set('source', filters.source)
    if (filters.location) params.set('location', filters.location)
    if (page > 1) params.set('page', page.toString())
    setSearchParams(params, { replace: true })
  }, [filters, search, page, setSearchParams])

  const handleSearch = (searchTerm) => {
    setSearch(searchTerm)
    setPage(1)
  }

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setPage(1)
  }

  const handlePageChange = (newPage) => {
    setPage(newPage)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const totalPages = data?.total_pages || 0

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Browse Jobs</h1>
        <JobSearch onSearch={handleSearch} initialValue={search} />
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Sidebar */}
        <aside className="lg:w-64 flex-shrink-0">
          <JobFilters
            filters={filters}
            onFilterChange={handleFilterChange}
            jobCounts={data?.counts || {}}
          />
        </aside>

        {/* Main Content */}
        <main className="flex-grow">
          {/* Results Header */}
          <div className="flex justify-between items-center mb-4">
            <p className="text-gray-600">
              {isLoading ? (
                'Loading...'
              ) : data?.total ? (
                <>
                  Showing{' '}
                  <span className="font-medium">
                    {(page - 1) * DEFAULT_PAGE_SIZE + 1}-
                    {Math.min(page * DEFAULT_PAGE_SIZE, data.total)}
                  </span>{' '}
                  of <span className="font-medium">{data.total}</span> jobs
                </>
              ) : (
                'No jobs found'
              )}
            </p>
          </div>

          {/* Job List */}
          <JobList jobs={data?.data} isLoading={isLoading} error={error} />

          {/* Pagination */}
          {totalPages > 1 && (
            <Pagination
              page={page}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              className="mt-8"
            />
          )}
        </main>
      </div>
    </div>
  )
}

export default JobsPage
