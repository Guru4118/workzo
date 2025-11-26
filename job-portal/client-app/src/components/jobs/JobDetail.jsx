import { Link } from 'react-router-dom'
import {
  HiOutlineLocationMarker,
  HiOutlineBriefcase,
  HiOutlineClock,
  HiOutlineExternalLink,
  HiOutlineArrowLeft,
} from 'react-icons/hi'
import Badge from '../ui/Badge'
import Spinner from '../ui/Spinner'
import { formatDate, formatSource, getSourceColor } from '../../utils/formatters'

const JobDetail = ({ job, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="card p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Error loading job</h2>
        <p className="text-gray-600 mb-4">{error.message || 'Something went wrong.'}</p>
        <Link to="/jobs" className="btn-primary">
          Back to Jobs
        </Link>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="card p-8 text-center">
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Job not found</h2>
        <p className="text-gray-600 mb-4">This job listing may have been removed.</p>
        <Link to="/jobs" className="btn-primary">
          Back to Jobs
        </Link>
      </div>
    )
  }

  const {
    title,
    company,
    location,
    job_type,
    description,
    source,
    scraped_at,
    salary,
    url,
    tags,
  } = job

  return (
    <div>
      {/* Back Button */}
      <Link
        to="/jobs"
        className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
      >
        <HiOutlineArrowLeft className="h-5 w-5" />
        Back to Jobs
      </Link>

      <div className="card">
        {/* Header */}
        <div className="p-6 border-b border-gray-100">
          <div className="flex justify-between items-start gap-4 flex-wrap">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
              <p className="text-xl text-primary-600 font-medium mb-4">{company}</p>

              {/* Meta Info */}
              <div className="flex flex-wrap gap-4 text-gray-600">
                {location && (
                  <span className="flex items-center gap-1.5">
                    <HiOutlineLocationMarker className="h-5 w-5" />
                    {location}
                  </span>
                )}
                {job_type && (
                  <span className="flex items-center gap-1.5">
                    <HiOutlineBriefcase className="h-5 w-5" />
                    {job_type}
                  </span>
                )}
                <span className="flex items-center gap-1.5">
                  <HiOutlineClock className="h-5 w-5" />
                  Posted {formatDate(scraped_at)}
                </span>
              </div>

              {/* Salary */}
              {salary && (
                <p className="text-lg text-green-600 font-semibold mt-4">{salary}</p>
              )}
            </div>

            {/* Source Badge */}
            <Badge color={getSourceColor(source)} className="text-sm">
              {formatSource(source)}
            </Badge>
          </div>
        </div>

        {/* Tags */}
        {tags && tags.length > 0 && (
          <div className="px-6 py-4 border-b border-gray-100">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Skills & Tags</h3>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag, index) => (
                <Badge key={index} color="gray">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        <div className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Description</h3>
          <div
            className="prose prose-gray max-w-none"
            dangerouslySetInnerHTML={{ __html: description || 'No description available.' }}
          />
        </div>

        {/* Apply Button */}
        {url && (
          <div className="px-6 pb-6">
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary inline-flex items-center gap-2"
            >
              Apply Now
              <HiOutlineExternalLink className="h-5 w-5" />
            </a>
          </div>
        )}
      </div>
    </div>
  )
}

export default JobDetail
