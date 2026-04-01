<template>
  <div class="layout">
    <aside class="side">
      <div class="brand">用户管理</div>
      <nav class="nav">
        <RouterLink class="nav-link" to="/admin/users" active-class="active">用户列表</RouterLink>
        <RouterLink class="nav-link" to="/admin/profile" active-class="active">我的资料</RouterLink>
      </nav>
      <div class="side-foot">
        <span class="who">{{ auth.user?.username || '—' }}</span>
        <button type="button" class="btn-ghost" @click="onLogout">退出</button>
      </div>
    </aside>
    <div class="main">
      <header class="top">
        <h1 class="title">{{ title }}</h1>
      </header>
      <main class="content">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const title = computed(() => route.meta.title || '管理后台')

function onLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.side {
  width: 220px;
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 1.25rem 0;
}

.brand {
  padding: 0 1.25rem 1rem;
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: -0.02em;
  color: var(--text);
}

.nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 0 0.75rem;
  flex: 1;
}

.nav-link {
  padding: 0.65rem 0.85rem;
  border-radius: var(--radius);
  color: var(--muted);
  text-decoration: none;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.nav-link:hover {
  background: var(--surface-hover);
  color: var(--text);
  text-decoration: none;
}

.nav-link.active {
  background: var(--accent-dim);
  color: var(--accent);
}

.side-foot {
  padding: 1rem 1.25rem 0;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.who {
  font-size: 0.85rem;
  color: var(--muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-ghost {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 0.45rem 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
}

.btn-ghost:hover {
  border-color: var(--muted);
  color: var(--text);
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.top {
  padding: 1.25rem 1.75rem;
  border-bottom: 1px solid var(--border);
  background: rgba(26, 35, 50, 0.6);
  backdrop-filter: blur(8px);
}

.title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.content {
  padding: 1.5rem 1.75rem 2rem;
  flex: 1;
}
</style>
