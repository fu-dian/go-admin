function pushResult(results, name, fn) {
  try {
    const ok = fn()
    results.push({ name, ok: !!ok, error: ok ? '' : '断言未通过' })
  } catch (e) {
    results.push({ name, ok: false, error: e?.message || String(e) })
  }
}

/** 与后端题目 id 对应，评测在浏览器内执行 */
export const runTestsById = {
  'two-sum'(solve) {
    const results = []
    pushResult(results, '用例1: [2,7,11,15], target=9', () => {
      const nums = [2, 7, 11, 15]
      const r = solve([...nums], 9)
      return (
        Array.isArray(r) &&
        r.length === 2 &&
        r[0] !== r[1] &&
        nums[r[0]] + nums[r[1]] === 9
      )
    })
    pushResult(results, '用例2: [3,2,4], target=6', () => {
      const nums = [3, 2, 4]
      const r = solve([...nums], 6)
      return (
        Array.isArray(r) &&
        r.length === 2 &&
        nums[r[0]] + nums[r[1]] === 6
      )
    })
    return results
  },
  'max-subarray'(solve) {
    const results = []
    pushResult(results, '用例1', () => solve([-2, 1, -3, 4, -1, 2, 1, -5, 4]) === 6)
    pushResult(results, '用例2 单元素', () => solve([1]) === 1)
    pushResult(results, '用例3 全负', () => solve([-3, -2, -1]) === -1)
    return results
  },
  'climb-stairs'(solve) {
    const results = []
    pushResult(results, 'n=5 → 8', () => solve(5) === 8)
    pushResult(results, 'n=3 → 3', () => solve(3) === 3)
    pushResult(results, 'n=1 → 1', () => solve(1) === 1)
    return results
  },
  'binary-search'(solve) {
    const results = []
    pushResult(results, '找到目标', () => solve([-1, 0, 3, 5, 9, 12], 9) === 4)
    pushResult(results, '不存在', () => solve([-1, 0, 3, 5, 9, 12], 2) === -1)
    pushResult(results, '单元素命中', () => solve([5], 5) === 0)
    return results
  },
  'longest-substring'(solve) {
    const results = []
    pushResult(results, '"abcabcbb" → 3', () => solve('abcabcbb') === 3)
    pushResult(results, '"bbbbb" → 1', () => solve('bbbbb') === 1)
    pushResult(results, '空串 → 0', () => solve('') === 0)
    return results
  },
  'coin-change'(solve) {
    const results = []
    pushResult(results, '[1,2,5], 11 → 3', () => {
      const r = solve([1, 2, 5], 11)
      return r === 3
    })
    pushResult(results, '[2], 3 → -1', () => solve([2], 3) === -1)
    pushResult(results, '[1], 0 → 0', () => solve([1], 0) === 0)
    return results
  },
  'trap-rain-water'(solve) {
    const results = []
    pushResult(results, '经典用例 → 6', () => {
      const h = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
      return solve(h) === 6
    })
    pushResult(results, '全 0 → 0', () => solve([0, 0, 0]) === 0)
    pushResult(results, '单调不降 → 0', () => solve([1, 2, 3, 4]) === 0)
    return results
  },
  'max-product-subarray'(solve) {
    const results = []
    pushResult(results, '[-2,3,-4] → 24', () => solve([-2, 3, -4]) === 24)
    pushResult(results, '[2,3,-2,4] → 6', () => solve([2, 3, -2, 4]) === 6)
    pushResult(results, '[-2,0,-1] → 0', () => solve([-2, 0, -1]) === 0)
    return results
  },
  'merge-intervals'(solve) {
    const results = []
    pushResult(results, '用例1', () => {
      const r = solve([
        [1, 3],
        [2, 6],
        [8, 10],
        [15, 18],
      ])
      const exp = [
        [1, 6],
        [8, 10],
        [15, 18],
      ]
      return JSON.stringify(r) === JSON.stringify(exp)
    })
    pushResult(results, '用例2 完全重叠', () => {
      const r = solve([[1, 4], [4, 5]])
      return JSON.stringify(r) === JSON.stringify([[1, 5]])
    })
    return results
  },
}

export function attachRunTests(meta) {
  if (!meta) return null
  const run = runTestsById[meta.id]
  return {
    ...meta,
    runTests:
      run ||
      (() => [{ name: '评测', ok: false, error: '本地未配置该题评测' }]),
  }
}
