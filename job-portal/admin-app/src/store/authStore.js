import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import authApi from '../api/auth'

const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (username, password) => {
        set({ isLoading: true, error: null })
        try {
          const data = await authApi.login(username, password)
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)

          // Get user info
          const user = await authApi.getMe()
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          })
          return true
        } catch (error) {
          const message =
            error.response?.data?.detail || 'Login failed. Please try again.'
          set({
            error: message,
            isLoading: false,
            isAuthenticated: false,
            user: null,
          })
          return false
        }
      },

      logout: async () => {
        try {
          await authApi.logout()
        } catch (error) {
          // Ignore logout errors
        } finally {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          })
        }
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ isAuthenticated: false, user: null })
          return false
        }

        try {
          const user = await authApi.getMe()
          set({
            user,
            isAuthenticated: true,
            error: null,
          })
          return true
        } catch (error) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          set({
            user: null,
            isAuthenticated: false,
            error: null,
          })
          return false
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)

export default useAuthStore
