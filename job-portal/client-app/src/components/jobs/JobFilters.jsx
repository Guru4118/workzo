import { useState } from 'react'
import { JOB_SOURCES } from '../../utils/constants'
import { formatSource } from '../../utils/formatters'

const JobFilters = ({ filters, onFilterChange, jobCounts = {} }) => {
  const { source, location } = filters
  const [locationInput, setLocationInput] = useState(location || '')

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value })
  }

  const handleLocationSubmit = (e) => {
    e.preventDefault()
    handleChange('location', locationInput || null)
  }

  return (
    <div className="card p-4">
      <h3 className="font-semibold text-gray-900 mb-4">Filters</h3>

      {/* Source Filter */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Job Source
        </label>
        <select
          value={source || ''}
          onChange={(e) => handleChange('source', e.target.value || null)}
          className="input"
        >
          <option value="">All Sources</option>
          {JOB_SOURCES.map((s) => (
            <option key={s} value={s}>
              {formatSource(s)} {jobCounts[s] ? `(${jobCounts[s]})` : ''}
            </option>
          ))}
        </select>
      </div>

      {/* Location Filter */}
      <form onSubmit={handleLocationSubmit} className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Location
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={locationInput}
            onChange={(e) => setLocationInput(e.target.value)}
            placeholder="e.g. Bangalore, Remote"
            className="input flex-1"
          />
          <button
            type="submit"
            className="px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
          >
            Apply
          </button>
        </div>
      </form>

      {/* Clear Filters */}
      <button
        onClick={() => {
          setLocationInput('')
          onFilterChange({ source: null, location: null })
        }}
        className="text-sm text-primary-600 hover:text-primary-700 font-medium"
      >
        Clear All Filters
      </button>
    </div>
  )
}

export default JobFilters
