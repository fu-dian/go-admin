<template>
  <div class="chat-container">
    <div class="chat-header">
      <h1 style="color: black;">小浮</h1>
      <div class="header-actions">
        <div v-if="!isLoggedIn" class="auth-buttons">
          <button style="color: black;" class="login-button" @click="showLoginModal = true">登录</button>
          <button style="color: black;" class="register-button" @click="showRegisterModal = true">注册</button>
        </div>
        <div v-else class="user-info">
          <span>{{ username }}</span>
          <button class="logout-button" @click="logout">退出</button>
        </div>
        <button style="color: black;" class="back-button" @click="goBack">返回首页</button>
      </div>
    </div>

    <div class="chat-content">
      <!-- 历史记录面板 -->
      <div class="history-panel">
        <div class="history-header">
          <h3 style="color: black;">历史记录</h3>
          <button class="clear-history-button" @click="clearHistory">清空</button>
        </div>
        <div class="history-list">
          <div v-for="(item, index) in history" :key="index" class="history-item" @click="loadHistory(item)">
            <div style="color: black;" class="history-question">{{ item.question }}</div>
            <div style="color: black;" class="history-time">{{ formatTime(item.timestamp) }}</div>
            <button class="delete-history-button" @click.stop="deleteHistory(index)">&times;</button>
          </div>
          <div v-if="history.length === 0" class="empty-history">暂无历史记录</div>
        </div>
      </div>

      <!-- 聊天区域 -->
      <div class="chat-main">
        <div class="chat-messages">
          <div v-for="(msg, index) in messages" :key="index" class="message-item">
            <div :class="msg.role === 'user' ? 'user-msg' : 'assistant-msg'">
              <div class="message-role">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
              <div v-html="marked.parse(msg.content)"></div>
            </div>
          </div>
          <div v-if="loading" class="loading">正在思考...</div>
        </div>

        <div class="input-area">
          <textarea v-model="inputText" @keydown.enter.exact="sendMessage" @keydown.enter.shift="inputText += '\n'"
            placeholder="请输入您的问题..."></textarea>
        </div>
      </div>
    </div>

    <!-- 登录弹窗 -->
    <div v-if="showLoginModal" class="modal-overlay" @click="closeLoginModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>用户登录</h2>
          <button class="close-button" @click="closeLoginModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleLogin">
            <div class="form-group">
              <label for="username">用户名</label>
              <input type="text" id="username" v-model="loginForm.username" placeholder="请输入用户名" required>
            </div>
            <div class="form-group">
              <label for="password">密码</label>
              <input type="password" id="password" v-model="loginForm.password" placeholder="请输入密码" required>
            </div>
            <div class="form-actions">
              <button type="submit" class="login-submit-button" :disabled="isLoggingIn">
                {{ isLoggingIn ? '登录中...' : '登录' }}
              </button>
              <div class="auth-switch">
                还没有账号？ <a href="#" @click.prevent="switchToRegister">立即注册</a>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 注册弹窗 -->
    <div v-if="showRegisterModal" class="modal-overlay" @click="closeRegisterModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>用户注册</h2>
          <button class="close-button" @click="closeRegisterModal">&times;</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleRegister">
            <div class="form-group">
              <label for="register-username">用户名</label>
              <input type="text" id="register-username" v-model="registerForm.username" placeholder="请输入用户名" required>
            </div>
            <div class="form-group">
              <label for="register-password">密码</label>
              <input type="password" id="register-password" v-model="registerForm.password" placeholder="请输入密码"
                required>
            </div>
            <div class="form-group">
              <label for="register-role">身份</label>
              <select id="register-role" v-model="registerForm.role" required>
                <option v-for="option in roleOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
            <div class="form-actions">
              <button type="submit" class="login-submit-button" :disabled="isRegistering">
                {{ isRegistering ? '注册中...' : '注册' }}
              </button>
              <div class="auth-switch">
                已有账号？ <a href="#" @click.prevent="switchToLogin">立即登录</a>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { marked } from 'marked'
import { authService } from '../api/auth'
import type { LoginForm, RegisterForm, User } from '../types'

const router = useRouter()
const route = useRoute()
const messages = ref([
  {
    role: 'assistant',
    content: '你好！我是AI助手，有什么可以帮助你的吗？'
  }
])
const inputText = ref('')
const loading = ref(false)

// 登录相关状态
const showLoginModal = ref(false)
const showRegisterModal = ref(false)
const isLoggedIn = ref(false)
const username = ref('')
const userRole = ref('user')
const isLoggingIn = ref(false)
const isRegistering = ref(false)
const loginForm = ref<LoginForm>({
  username: '',
  password: ''
})
const registerForm = ref<RegisterForm>({
  username: '',
  password: '',
  role: 'user'
})

// 身份选项
const roleOptions = [
  { value: 'user', label: '普通用户' },
  { value: 'teacher', label: '教师' },
  { value: 'doctor', label: '医生' },
  { value: 'engineer', label: '工程师' },
  { value: 'student', label: '学生' }
]

// 历史记录相关
interface HistoryItem {
  question: string;
  answer: string;
  timestamp: number;
}

const history = ref<HistoryItem[]>([])

onMounted(() => {
  // 检查登录状态
  checkLoginStatus()
  // 加载历史记录
  loadHistoryFromLocalStorage()

  // 检查URL参数中是否有消息，如果有则自动发送
  const initialMessage = route.query.message
  if (initialMessage) {
    inputText.value = initialMessage
    sendMessage()
  }
})

// 从本地存储加载历史记录
const loadHistoryFromLocalStorage = () => {
  try {
    const storedHistory = localStorage.getItem('chatHistory')
    if (storedHistory) {
      history.value = JSON.parse(storedHistory)
    }
  } catch (error) {
    console.error('加载历史记录失败:', error)
  }
}

// 保存历史记录到本地存储
const saveHistoryToLocalStorage = () => {
  try {
    localStorage.setItem('chatHistory', JSON.stringify(history.value))
  } catch (error) {
    console.error('保存历史记录失败:', error)
  }
}

// 保存当前对话到历史记录
const saveToHistory = (question: string, answer: string) => {
  const newHistoryItem: HistoryItem = {
    question,
    answer,
    timestamp: Date.now()
  }

  // 添加到历史记录开头
  history.value.unshift(newHistoryItem)

  // 限制历史记录数量
  if (history.value.length > 20) {
    history.value = history.value.slice(0, 20)
  }

  // 保存到本地存储
  saveHistoryToLocalStorage()
}

// 加载历史记录
const loadHistory = (item: HistoryItem) => {
  // 清空当前消息
  messages.value = [
    {
      role: 'assistant',
      content: '你好！我是AI助手，有什么可以帮助你的吗？'
    },
    {
      role: 'user',
      content: item.question
    },
    {
      role: 'assistant',
      content: item.answer
    }
  ]
}

// 删除历史记录
const deleteHistory = (index: number) => {
  history.value.splice(index, 1)
  saveHistoryToLocalStorage()
}

// 清空历史记录
const clearHistory = () => {
  history.value = []
  saveHistoryToLocalStorage()
}

// 格式化时间
const formatTime = (timestamp: number) => {
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goBack = () => {
  router.push('/')
}

// 检查登录状态
const checkLoginStatus = () => {
  const user = authService.getUserFromLocalStorage()
  if (user) {
    isLoggedIn.value = true
    username.value = user.username
    userRole.value = user.role
  }
}

// 打开登录弹窗
const openLoginModal = () => {
  showLoginModal.value = true
  showRegisterModal.value = false
}

// 关闭登录弹窗
const closeLoginModal = () => {
  showLoginModal.value = false
  loginForm.value = {
    username: '',
    password: ''
  }
  isLoggingIn.value = false
}

// 打开注册弹窗
const openRegisterModal = () => {
  showRegisterModal.value = true
  showLoginModal.value = false
}

// 关闭注册弹窗
const closeRegisterModal = () => {
  showRegisterModal.value = false
  registerForm.value = {
    username: '',
    password: ''
  }
  isRegistering.value = false
}

// 切换到注册
const switchToRegister = () => {
  closeLoginModal()
  openRegisterModal()
}

// 切换到登录
const switchToLogin = () => {
  closeRegisterModal()
  openLoginModal()
}

// 处理登录
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) return

  isLoggingIn.value = true

  try {
    // 调用后端登录API
    const user = await authService.login(loginForm.value)

    // 存储用户信息
    authService.saveUserToLocalStorage(user)

    // 更新登录状态
    isLoggedIn.value = true
    username.value = user.username
    userRole.value = user.role

    // 关闭弹窗
    closeLoginModal()

    // 显示登录成功消息
    messages.value.push({
      role: 'assistant',
      content: `欢迎回来，${user.username}！有什么可以帮助你的吗？`
    })
  } catch (error) {
    console.error('登录失败:', error)
    alert('登录失败，请检查用户名和密码')
  } finally {
    isLoggingIn.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.password) return

  isRegistering.value = true

  try {
    // 调用后端注册API
    const user = await authService.register(registerForm.value)

    // 存储用户信息
    authService.saveUserToLocalStorage(user)

    // 更新登录状态
    isLoggedIn.value = true
    username.value = user.username
    userRole.value = user.role

    // 关闭弹窗
    closeRegisterModal()

    // 显示注册成功消息
    messages.value.push({
      role: 'assistant',
      content: `欢迎，${user.username}！注册成功，有什么可以帮助你的吗？`
    })
  } catch (error) {
    console.error('注册失败:', error)
    alert('注册失败，请检查用户名是否已存在')
  } finally {
    isRegistering.value = false
  }
}

// 退出登录
const logout = () => {
  authService.removeUserFromLocalStorage()
  isLoggedIn.value = false
  username.value = ''

  // 显示退出登录消息
  messages.value.push({
    role: 'assistant',
    content: '您已退出登录。如果需要继续使用，请重新登录。'
  })
}

const sendMessage = async () => {
  if (!inputText.value.trim() || loading.value) return

  // 添加用户消息
  messages.value.push({
    role: 'user',
    content: inputText.value
  })

  const userInput = inputText.value
  inputText.value = ''
  loading.value = true

  // 创建AI消息占位符
  const aiMessageIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: ''
  })

  try {
    // 调用后端API（流式）
    const response = await fetch('http://localhost:8080/api/v1/agent/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messages: [
          {
            role: 'user',
            content: userInput
          }
        ]
      })
    })

    if (!response.ok) {
      throw new Error('API调用失败')
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('无法获取响应流')
    }

    const decoder = new TextDecoder()

    // 处理流式响应
    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        const trimmedLine = line.trim()
        if (trimmedLine === '') continue
        if (trimmedLine === 'data: [DONE]') continue

        if (trimmedLine.startsWith('data: ')) {
          const data = trimmedLine.substring(6)
          try {
            // 直接添加内容
            messages.value[aiMessageIndex].content += data
          } catch (error) {
            console.error('解析流式数据失败:', error)
          }
        }
      }
    }

    // 保存到历史记录
    saveToHistory(userInput, messages.value[aiMessageIndex].content)
  } catch (error) {
    console.error('Error:', error)
    messages.value[aiMessageIndex].content = '抱歉，我暂时无法回答您的问题，请稍后再试。'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* 样式部分保持不变 */
.chat-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  overflow: hidden;
}

.chat-header {
  height: 70px;
  background: white;
  backdrop-filter: blur(10px);
  color: #333;
  padding: 20px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border-bottom: 1px solid #e0e0e0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.auth-buttons {
  display: flex;
  gap: 10px;
  align-items: center;
}

.login-button,
.register-button,
.logout-button {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;

}

.login-button {
  font-weight: 500;
  background: white;
  color: #333;
}

.login-button:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
}

.register-button {
  font-weight: 500;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.logout-button {
  background: #f5f5f5;
  color: #333;
  border-color: #e0e0e0;
}

.logout-button:hover {
  background: #e0e0e0;
  transform: translateY(-2px);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.back-button {
  padding: 8px 16px;
  font-weight: 500;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #333;
}

.back-button:hover {
  background: #f5f5f5;
  transform: translateY(-2px);
}

/* 聊天内容区域 */
.chat-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 历史记录面板 */
.history-panel {
  width: 20%;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-header {
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.clear-history-button {
  padding: 4px 12px;
  font-weight: 500;
  background: #f5f5f5;
  color: #333;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-history-button:hover {
  background: #e0e0e0;
}

.history-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  background: white;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.history-item:hover {
  background: #e8e8e8;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.history-question {
  font-size: 14px;
  color: #333;
  margin-bottom: 6px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.history-time {
  font-size: 12px;
  color: #999;
}

.delete-history-button {
  position: absolute;
  top: 8px;
  right: 8px;
  background: #f5f5f5;
  color: #999;
  border: none;
  border-radius: 5px;
  width: 20px;
  height: 20px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.delete-history-button:hover {
  background: #ff4d4d;
  color: white;
}

.empty-history {
  color: #999;
  font-size: 14px;
  text-align: center;
  margin-top: 40px;
  padding: 20px;
}

/* 聊天主区域 */
.chat-main {
  width: 80%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

/* 登录弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  animation: modalFadeIn 0.3s ease;
}

@keyframes modalFadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  transition: color 0.3s ease;
}

.close-button:hover {
  color: #333;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-actions {
  margin-top: 30px;
  text-align: center;
}

.login-submit-button {
  width: 100%;
  padding: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.login-submit-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.login-submit-button:disabled {
  background: #a0a0a0;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.auth-switch {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
  color: #666;
}

.auth-switch a {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.auth-switch a:hover {
  color: #764ba2;
  text-decoration: underline;
}

.chat-header h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  letter-spacing: 1px;
}

.back-button {
  padding: 8px 16px;
  background: white;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-2px);
}

.chat-messages {
  flex: 1;
  padding: 20px 180px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

.message-item {
  margin: 20px 0;
  display: flex;
  flex-direction: column;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-msg {
  align-self: flex-end;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  border-radius: 20px 20px 4px 20px;
  max-width: 75%;
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
}

.assistant-msg {
  align-self: flex-start;
  background: white;
  padding: 16px 20px;
  border-radius: 4px 20px 20px 20px;
  max-width: 75%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  border: 1px solid #e0e0e0;
  color: black;
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #666;
  opacity: 0.8;
}

.user-msg .message-role {
  color: rgba(255, 255, 255, 0.8);
  text-align: right;
}

.input-area {
  padding: 20px 120px;
  margin: 0 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 15px;
  align-items: flex-end;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
  border-radius: 12px;
  margin-bottom: 20px;
}

textarea {
  flex: 1;
  height: 100px;
  padding: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  resize: none;
  font-size: 16px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

button {
  padding: 0 32px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

button:disabled {
  background: #a0a0a0;
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.loading {
  text-align: center;
  padding: 15px;
  color: #666;
  font-style: italic;
  font-size: 14px;
}

.loading::after {
  content: '';
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid #667eea;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s ease-in-out infinite;
  margin-left: 10px;
  vertical-align: middle;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar {
  width: 8px;
  position: absolute;
  right: 0;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  transition: background 0.3s ease;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-header {
    padding: 15px 20px;
  }

  .chat-header h1 {
    font-size: 24px;
  }

  .chat-content {
    flex-direction: column;
  }

  .history-panel {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  }

  .chat-main {
    width: 100%;
    flex: 1;
  }

  .chat-messages {
    padding: 20px;
  }

  .input-area {
    padding: 15px 20px;
  }

  .user-msg,
  .assistant-msg {
    max-width: 85%;
  }
}
</style>