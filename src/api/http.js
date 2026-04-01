import axios from 'axios'

const http = axios.create({
  baseURL: '/api/v1',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 从本地存储获取令牌
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        const user = JSON.parse(userStr)
        if (user.token) {
          config.headers.Authorization = `Bearer ${user.token}`
        }
      } catch (error) {
        console.error('解析用户信息失败:', error)
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 简化的响应拦截器
http.interceptors.response.use(
  (res) => {
    const body = res.data
    if (body && typeof body === 'object' && 'code' in body) {
      const { code, msg, data } = body
      if (code >= 200 && code < 300) {
        res.data = data
        return res
      }
      return Promise.reject(new Error(msg || '请求失败'))
    }
    return res
  },
  (err) => {
    const payload = err.response?.data
    const msg =
      (typeof payload === 'object' && payload?.msg) ||
      err.message ||
      '网络错误'

    return Promise.reject(new Error(msg))
  }
)

export default http
