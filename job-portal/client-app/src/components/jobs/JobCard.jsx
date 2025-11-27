import { Link } from 'react-router-dom'
import {
  HiOutlineLocationMarker,
  HiOutlineBriefcase,
  HiOutlineClock,
  HiOutlineExternalLink
} from 'react-icons/hi'
import Badge from '../ui/Badge'
import { formatDate, truncate, formatSource, getSourceColor } from '../../utils/formatters'

const JobCard = ({ job }) => {
  const {
    id,
    title,
    company,
    location,
    job_type,
    description,
    source,
    scraped_at,
    salary,
    apply_url
  } = job

  return (
    <Link
      to={`/jobs/${id}`}
      className="card block hover:shadow-md transition-shadow duration-200 p-6"
    >
      <div className="flex justify-between items-start gap-4">
        <div className="flex-grow min-w-0">
          {/* Title and Company */}
          <h3 className="text-lg font-semibold text-gray-900 mb-1 truncate">
            {title}
          </h3>
          <p className="text-primary-600 font-medium mb-3">{company}</p>

          {/* Meta Info */}
          <div className="flex flex-wrap gap-3 text-sm text-gray-500 mb-3">
            {location && (
              <span className="flex items-center gap-1">
                <HiOutlineLocationMarker className="h-4 w-4" />
                {location}
              </span>
            )}
            {job_type && (
              <span className="flex items-center gap-1">
                <HiOutlineBriefcase className="h-4 w-4" />
                {job_type}
              </span>
            )}
            <span className="flex items-center gap-1">
              <HiOutlineClock className="h-4 w-4" />
              {formatDate(scraped_at)}
            </span>
          </div>

          {/* Description Preview */}
          {description && (
            <p className="text-gray-600 text-sm line-clamp-2">
              {truncate(description, 150)}
            </p>
          )}

          {/* Footer */}
          <div className="mt-4 flex items-center justify-between">
            {salary && (
              <p className="text-green-600 font-medium text-sm">
                {salary}
              </p>
            )}

            {/* ✅ Apply Button */}
            {apply_url && (
              <a
                href={apply_url}
                target="_blank"
                rel="noopener noreferrer"
                onClick={(e) => e.stopPropagation()}
                className="inline-flex items-center gap-1 text-sm font-medium text-blue-600 hover:text-blue-800"
              >
                Apply
                <HiOutlineExternalLink className="h-4 w-4" />
              </a>
            )}
          </div>
        </div>

        {/* Source Badge */}
        <Badge color={getSourceColor(source)} className="flex-shrink-0">
          {formatSource(source)}
        </Badge>
      </div>
    </Link>
  )
}

export default JobCard
