/** 难度标签；题目元数据由后端 GET /problems 提供，评测用例在 algorithmProblemRunners.js */

export const DIFFICULTY_LABEL = {
  easy: '简单',
  medium: '中等',
  hard: '困难',
}

/** UTC 日期序数（与本地「今天」一致用于每日一题） */
export function dayIndexUTC(d = new Date()) {
  return Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000)
}

/** @param {'javascript'|'python'|'cpp'} lang */
export function getStarterForLang(problem, lang) {
  if (!problem) return ''
  if (lang === 'python') return problem.pythonStarter || problem.starterCode
  if (lang === 'cpp') return problem.cppStarter || '// 暂无模板'
  return problem.starterCode
}
