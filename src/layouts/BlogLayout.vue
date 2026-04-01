<template>
  <div class="blog-root">
    <header class="blog-header">
      <RouterLink class="logo" to="/blog">每日算法刷题</RouterLink>
      <nav class="blog-nav">
        <RouterLink to="/blog" class="nav-item" active-class="active" end>今日一题</RouterLink>
        <RouterLink to="/blog/history" class="nav-item" active-class="active">做题历史</RouterLink>
        <RouterLink to="/blog/profile" class="nav-item" active-class="active">我的资料</RouterLink>
      </nav>
      <div class="blog-actions">
        <span class="nick">{{ auth.user?.username || '—' }}</span>
        <button type="button" class="btn-out" @click="onLogout">退出</button>
      </div>
    </header>
    <div class="blog-body">
      <aside class="agent-aside" aria-label="智能体助手">
        <AgentPanel />
      </aside>
      <main class="blog-main">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import AgentPanel from '@/components/AgentPanel.vue'

const router = useRouter()
const auth = useAuthStore()

function onLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.blog-root {
  min-height: 100vh;
  background: #faf7f2;
  color: #1c1917;
  display: flex;
  flex-direction: column;
}

.blog-body {
  display: flex;
  flex: 1;
  align-items: stretch;
  min-height: 0;
}

.agent-aside {
  width: min(360px, 34vw);
  flex-shrink: 0;
  border-right: 1px solid #e7e2d9;
  background: #fff;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.blog-main {
  flex: 1;
  min-width: 0;
  overflow: auto;
}

.blog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e7e2d9;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(8px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.logo {
  font-family: 'Georgia', 'Times New Roman', serif;
  font-weight: 700;
  font-size: 1.2rem;
  color: #0f766e;
  text-decoration: none;
}

.logo:hover {
  text-decoration: none;
  color: #115e59;
}

.blog-nav {
  display: flex;
  gap: 0.5rem;
}

.nav-item {
  padding: 0.4rem 0.75rem;
  border-radius: 6px;
  color: #57534e;
  text-decoration: none;
  font-size: 0.95rem;
}

.nav-item:hover {
  background: #f5f0e8;
  text-decoration: none;
}

.nav-item.active {
  background: #ccfbf1;
  color: #0f766e;
}

.blog-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nick {
  font-size: 0.9rem;
  color: #78716c;
}

.btn-out {
  background: transparent;
  border: 1px solid #d6d3d1;
  color: #44403c;
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
}

.btn-out:hover {
  border-color: #a8a29e;
}
</style>
