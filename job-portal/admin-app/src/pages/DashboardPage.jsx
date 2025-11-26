import { Link } from 'react-router-dom'
import {
  HiOutlineClipboardCheck,
  HiOutlineCheck,
  HiOutlineX,
  HiOutlineCollection,
} from 'react-icons/hi'
import { useAdminStats } from '../hooks/useJobs'

const StatCard = ({ icon: Icon, label, value, color, to }) => {
  const content = (
    <div className="card p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${color}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div>
          <p className="text-gray-500 text-sm">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value ?? '-'}</p>
        </div>
      </div>
    </div>
  )

  if (to) {
    return <Link to={to}>{content}</Link>
  }
  return content
}

const DashboardPage = () => {
  const { data: stats, isLoading, error } = useAdminStats()

  if (error) {
    return (
      <div className="card p-6 text-center">
        <p className="text-red-600">Error loading stats: {error.message}</p>
      </div>
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Dashboard</h2>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={HiOutlineCollection}
          label="Total Raw Jobs"
          value={isLoading ? '...' : stats?.total_raw}
          color="bg-blue-100 text-blue-600"
        />
        <StatCard
          icon={HiOutlineClipboardCheck}
          label="Pending Review"
          value={isLoading ? '...' : stats?.total_pending}
          color="bg-yellow-100 text-yellow-600"
          to="/pending"
        />
        <StatCard
          icon={HiOutlineCheck}
          label="Approved Jobs"
          value={isLoading ? '...' : stats?.total_approved}
          color="bg-green-100 text-green-600"
        />
        <StatCard
          icon={HiOutlineX}
          label="Rejected Jobs"
          value={isLoading ? '...' : stats?.total_rejected}
          color="bg-red-100 text-red-600"
        />
      </div>

      {/* Jobs by Source */}
      {stats?.jobs_by_source && (
        <div className="card p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Jobs by Source
          </h3>
          <div className="space-y-3">
            {Object.entries(stats.jobs_by_source).map(([source, count]) => (
              <div
                key={source}
                className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
              >
                <span className="text-gray-700 capitalize">{source}</span>
                <span className="font-medium text-gray-900">{count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage
