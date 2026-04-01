<template>
  <div class="agent-panel">
    <div class="agent-head">
      <h2 class="agent-title">刷题助手</h2>
      <p class="agent-sub">基于大模型，思路提示（不直接给完整题解）</p>
    </div>
    <div ref="scrollRef" class="agent-messages">
      <p v-if="!msgs.length" class="agent-empty">在右侧选题后可以问题意、思路或让助手看你的代码思路。</p>
      <div
        v-for="(m, i) in msgs"
        :key="i"
        class="msg"
        :class="m.role === 'user' ? 'user' : 'assistant'"
      >
        <span class="msg-role">{{ m.role === 'user' ? '你' : '助手' }}</span>
        <pre class="msg-body">{{ m.content }}</pre>
      </div>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
    <form class="agent-input-row" @submit.prevent="send">
      <textarea
        v-model="input"
        class="agent-input"
        rows="3"
        placeholder="输入问题，Enter 发送，Shift+Enter 换行"
        :disabled="loading"
        @keydown="onKeydown"
      />
      <button type="submit" class="agent-send" :disabled="loading || !input.trim()">
        {{ loading ? '请求中…' : '发送' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { nextTick, ref, watch } from 'vue'
import { postAgentChat } from '@/api/agent'
import { useAlgoContextStore } from '@/stores/algoContext'

const algo = useAlgoContextStore()
const msgs = ref([])
const input = ref('')
const loading = ref(false)
const err = ref('')
const scrollRef = ref(null)

watch(
  () => msgs.value.length,
  async () => {
    await nextTick()
    const el = scrollRef.value
    if (el) el.scrollTop = el.scrollHeight
  }
)

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

async function send() {
  const text = input.value.trim()
  if (!text || loading.value) return
  err.value = ''
  msgs.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  try {
    const problemId = algo.currentProblem?.id || ''
    const payload = msgs.value.map((m) => ({ role: m.role, content: m.content }))
    const data = await postAgentChat(payload, problemId)
    const reply = data?.reply ?? ''
    msgs.value.push({ role: 'assistant', content: reply || '（空回复）' })
  } catch (e) {
    err.value = e?.message || String(e)
    msgs.value.push({
      role: 'assistant',
      content: '请求失败：' + (e?.message || String(e)),
    })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.agent-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.agent-head {
  padding: 1rem 1rem 0.75rem;
  border-bottom: 1px solid #e7e2d9;
  flex-shrink: 0;
}

.agent-title {
  margin: 0;
  font-size: 1.05rem;
  color: #0f766e;
}

.agent-sub {
  margin: 0.35rem 0 0;
  font-size: 0.75rem;
  color: #78716c;
  line-height: 1.4;
}

.agent-messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 1rem;
  min-height: 200px;
}

.agent-empty {
  margin: 0;
  font-size: 0.85rem;
  color: #a8a29e;
  line-height: 1.5;
}

.msg {
  margin-bottom: 0.85rem;
}

.msg-role {
  display: block;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #78716c;
  margin-bottom: 0.25rem;
}

.msg.user .msg-role {
  color: #0d9488;
}

.msg-body {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 0.88rem;
  line-height: 1.55;
  color: #292524;
}

.err {
  font-size: 0.8rem;
  color: #b91c1c;
  margin: 0 0 0.5rem;
}

.agent-input-row {
  padding: 0.75rem 1rem 1rem;
  border-top: 1px solid #e7e2d9;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
  background: #fafaf9;
}

.agent-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.5rem 0.65rem;
  font-size: 0.875rem;
  border: 1px solid #d6d3d1;
  border-radius: 8px;
  resize: none;
  font-family: inherit;
}

.agent-input:focus {
  outline: none;
  border-color: #0d9488;
}

.agent-send {
  align-self: flex-end;
  background: #0d9488;
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 1rem;
  font-size: 0.9rem;
  cursor: pointer;
  font-weight: 600;
}

.agent-send:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}
</style>
