import JobCard from './JobCard'
import Spinner from '../ui/Spinner'
import EmptyState from '../ui/EmptyState'
import { HiOutlineBriefcase } from 'react-icons/hi'

const JobList = ({ jobs, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <EmptyState
        icon={HiOutlineBriefcase}
        title="Error loading jobs"
        description={error.message || 'Something went wrong. Please try again later.'}
      />
    )
  }

  if (!jobs || jobs.length === 0) {
    return (
      <EmptyState
        icon={HiOutlineBriefcase}
        title="No jobs found"
        description="We couldn't find any jobs matching your criteria. Try adjusting your filters."
      />
    )
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </div>
  )
}

export default JobList
