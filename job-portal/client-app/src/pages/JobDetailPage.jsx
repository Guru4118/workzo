import { useParams } from 'react-router-dom'
import { JobDetail } from '../components/jobs'
import { useJob } from '../hooks/useJobs'

const JobDetailPage = () => {
  const { id } = useParams()
  const { data: job, isLoading, error } = useJob(id)

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <JobDetail job={job} isLoading={isLoading} error={error} />
    </div>
  )
}

export default JobDetailPage
