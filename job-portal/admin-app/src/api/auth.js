import apiClient from './client'

export const authApi = {
  login: async (username, password) => {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await apiClient.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  logout: async () => {
    await apiClient.post('/auth/logout')
  },

  getMe: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  refresh: async (refreshToken) => {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}

export default authApi
