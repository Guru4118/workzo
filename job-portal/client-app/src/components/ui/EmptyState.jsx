import { HiOutlineSearch } from 'react-icons/hi'

const EmptyState = ({
  icon: Icon = HiOutlineSearch,
  title = 'No results found',
  description = 'Try adjusting your search or filter to find what you\'re looking for.',
  action,
  className = '',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 text-center ${className}`}>
      <div className="p-4 bg-gray-100 rounded-full mb-4">
        <Icon className="h-8 w-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-medium text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 max-w-md mb-4">{description}</p>
      {action}
    </div>
  )
}

export default EmptyState
