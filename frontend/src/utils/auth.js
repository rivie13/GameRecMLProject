/**
 * Auth utility functions
 */

export const setToken = (token) => {
  localStorage.setItem('access_token', token)
}

export const getToken = () => {
  return localStorage.getItem('access_token')
}

export const removeToken = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')
}

export const setUser = (user) => {
  localStorage.setItem('user', JSON.stringify(user))
}

export const getUser = () => {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

export const isAuthenticated = () => {
  return !!getToken()
}
