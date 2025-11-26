import { useState } from 'react'
import { HiOutlineSearch } from 'react-icons/hi'

const JobSearch = ({ onSearch, initialValue = '', placeholder = 'Search jobs...' }) => {
  const [searchTerm, setSearchTerm] = useState(initialValue)

  const handleSubmit = (e) => {
    e.preventDefault()
    onSearch(searchTerm.trim())
  }

  const handleChange = (e) => {
    setSearchTerm(e.target.value)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative">
        <HiOutlineSearch className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
        <input
          type="text"
          value={searchTerm}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="input pl-12 pr-24 py-3 text-base"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 btn-primary py-1.5 px-4 text-sm"
        >
          Search
        </button>
      </div>
    </form>
  )
}

export default JobSearch
