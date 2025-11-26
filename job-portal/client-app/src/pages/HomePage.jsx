import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { HiOutlineBriefcase, HiOutlineGlobe, HiOutlineSparkles } from 'react-icons/hi'
import { JobSearch } from '../components/jobs'
import { useJobs } from '../hooks/useJobs'
import JobCard from '../components/jobs/JobCard'
import Spinner from '../components/ui/Spinner'

const HomePage = () => {
  const navigate = useNavigate()
  const { data, isLoading } = useJobs({ perPage: 6 })

  const handleSearch = (searchTerm) => {
    navigate(`/jobs?search=${encodeURIComponent(searchTerm)}`)
  }

  const features = [
    {
      icon: HiOutlineBriefcase,
      title: 'Remote Jobs',
      description: 'Browse thousands of remote job opportunities from top companies.',
    },
    {
      icon: HiOutlineGlobe,
      title: 'Multiple Sources',
      description: 'Jobs aggregated from RemoteOK, Remotive, Arbeitnow, and more.',
    },
    {
      icon: HiOutlineSparkles,
      title: 'Fresh Listings',
      description: 'Updated regularly with the latest job postings.',
    },
  ]

  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl sm:text-5xl font-bold mb-6">
              Find Your Dream Remote Job
            </h1>
            <p className="text-xl text-primary-100 mb-8">
              Discover remote opportunities from the world's best companies.
              Your next career move starts here.
            </p>
            <div className="max-w-2xl mx-auto">
              <JobSearch
                onSearch={handleSearch}
                placeholder="Search by job title, company, or keywords..."
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center p-6">
                <div className="inline-flex items-center justify-center w-14 h-14 bg-primary-100 rounded-xl mb-4">
                  <feature.icon className="h-7 w-7 text-primary-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Recent Jobs Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-bold text-gray-900">Recent Jobs</h2>
            <a
              href="/jobs"
              className="text-primary-600 hover:text-primary-700 font-medium"
            >
              View All Jobs
            </a>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-12">
              <Spinner size="lg" />
            </div>
          ) : data?.data?.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {data.data.map((job) => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500">
              No jobs available at the moment.
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Ready to Find Your Next Opportunity?
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Browse through hundreds of remote job listings and find the perfect match for your skills.
          </p>
          <a href="/jobs" className="btn-primary text-lg px-8 py-3">
            Browse All Jobs
          </a>
        </div>
      </section>
    </div>
  )
}

export default HomePage
