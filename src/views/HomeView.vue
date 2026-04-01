<template>
  <div class="home-container">
    <div class="home-content">
      <h1>小浮对话助手</h1>
      <p>输入您的问题，开始与AI对话</p>
      <div class="input-section">
        <textarea 
          v-model="inputText" 
          @keydown.enter.exact="startChat"
          @keydown.enter.shift="inputText += '\n'"
          placeholder="请输入您的问题..."
        ></textarea>
        <button @click="startChat" :disabled="!inputText.trim()">开始对话</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import {postAgentChat} from '../api/agent.js'
const router = useRouter()
const inputText = ref('')

const startChat = async() => {
  if (!inputText.value.trim()) return
  const res = postAgentChat([{role: "user", content: "你好，你是谁？"}])
  console.log(res)
  // 导航到聊天页面，并传递输入的文本作为参数
  router.push({
    path: '/chat',
    query: { message: inputText.value }
  })
}
</script>

<style scoped>
.home-container {
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  overflow: hidden;
}

.home-content {
  max-width: 800px;
  width: 90%;
  text-align: center;
  color: white;
  animation: fadeIn 1s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.home-content h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 20px;
  letter-spacing: 2px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.home-content p {
  font-size: 20px;
  margin-bottom: 40px;
  opacity: 0.9;
}

.input-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
  animation: slideUp 0.8s ease 0.3s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

textarea {
  width: 100%;
  height: 150px;
  padding: 20px;
  border: none;
  border-radius: 16px;
  font-size: 18px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  resize: none;
}

textarea:focus {
  outline: none;
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

button {
  align-self: center;
  padding: 16px 48px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  border: none;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

button:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  background: white;
}

button:disabled {
  background: rgba(255, 255, 255, 0.6);
  cursor: not-allowed;
  transform: none;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home-content h1 {
    font-size: 36px;
  }
  
  .home-content p {
    font-size: 18px;
  }
  
  textarea {
    height: 120px;
    padding: 16px;
    font-size: 16px;
  }
  
  button {
    padding: 14px 40px;
    font-size: 16px;
  }
}
</style>