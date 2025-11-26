// Format date to readable string
export const formatDate = (dateString) => {
  if (!dateString) return 'Unknown date'

  try {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now - date)
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 0) return 'Today'
    if (diffDays === 1) return 'Yesterday'
    if (diffDays < 7) return `${diffDays} days ago`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`

    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateString
  }
}

// Truncate text with ellipsis
export const truncate = (text, maxLength = 100) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

// Strip HTML tags from string
export const stripHtml = (html) => {
  if (!html) return ''
  return html.replace(/<[^>]*>/g, '').trim()
}

// Format source name
export const formatSource = (source) => {
  if (!source) return 'Unknown'
  const sources = {
    remoteok: 'RemoteOK',
    remotive: 'Remotive',
    arbeitnow: 'Arbeitnow',
    indeed: 'Indeed',
  }
  return sources[source.toLowerCase()] || source.charAt(0).toUpperCase() + source.slice(1)
}

// Get source badge color
export const getSourceColor = (source) => {
  const colors = {
    remoteok: 'bg-green-100 text-green-800',
    remotive: 'bg-blue-100 text-blue-800',
    arbeitnow: 'bg-purple-100 text-purple-800',
    indeed: 'bg-orange-100 text-orange-800',
  }
  return colors[source?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}
