const KEY = 'daily_algo_history_v1'
const MAX = 300

/**
 * @typedef {{ id: string, problemId: string, title: string, difficulty: string, dateKey: string, passed: boolean, code: string, language?: string, at: number }} HistoryItem
 */

/** @returns {HistoryItem[]} */
export function loadHistory() {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) ? arr : []
  } catch {
    return []
  }
}

/** @param {Omit<HistoryItem, 'at'> & { at?: number }} rec */
export function saveHistoryRecord(rec) {
  const list = loadHistory()
  const item = {
    id: rec.id || `${rec.problemId}-${rec.at || Date.now()}`,
    problemId: rec.problemId,
    title: rec.title,
    difficulty: rec.difficulty,
    dateKey: rec.dateKey,
    passed: rec.passed,
    code: rec.code,
    language: rec.language,
    at: rec.at ?? Date.now(),
  }
  list.unshift(item)
  localStorage.setItem(KEY, JSON.stringify(list.slice(0, MAX)))
}

export function clearHistory() {
  localStorage.removeItem(KEY)
}

export function draftKey(problemId, lang = 'javascript') {
  return `daily_algo_draft_${problemId}_${lang}`
}

/** 兼容旧版仅按题目 id 存草稿 */
export function loadDraft(problemId, lang = 'javascript') {
  try {
    const k = draftKey(problemId, lang)
    let v = localStorage.getItem(k)
    if (!v && lang === 'javascript') {
      v = localStorage.getItem(`daily_algo_draft_${problemId}`) || ''
    }
    return v || ''
  } catch {
    return ''
  }
}

export function saveDraft(problemId, code, lang = 'javascript') {
  try {
    localStorage.setItem(draftKey(problemId, lang), code)
  } catch {
    /* ignore quota */
  }
}
