import { loadPyodideOnce } from './pyodideLoader.js'

/**
 * JavaScript：用户代码中必须定义 function solve(...)，与题目约定参数一致。
 */
export function runUserCode(code, problem) {
  try {
    const factory = new Function(`
      "use strict";
      ${code}
      if (typeof solve !== 'function') {
        throw new Error('请在编辑器中定义 function solve(...)')
      }
      return solve
    `)
    const solve = factory()
    return problem.runTests(solve)
  } catch (e) {
    return [{ name: '运行', ok: false, error: e?.message || String(e) }]
  }
}

function wrapPySolve(pyodide, pySolve) {
  return (...args) => {
    const converted = args.map((a) => {
      if (a === null || a === undefined) return a
      if (typeof a === 'number' || typeof a === 'string' || typeof a === 'boolean')
        return a
      return pyodide.toPy(a)
    })
    let res = pySolve(...converted)
    if (res != null && typeof res.toJs === 'function') {
      res = res.toJs()
    }
    return res
  }
}

async function runPythonCode(code, problem) {
  try {
    const pyodide = await loadPyodideOnce()
    await pyodide.runPythonAsync(code)
    const pySolve = pyodide.globals.get('solve')
    if (!pySolve) {
      return [
        {
          name: '运行',
          ok: false,
          error: '请定义 def solve(...):（与题面参数一致）',
        },
      ]
    }
    const solve = wrapPySolve(pyodide, pySolve)
    return problem.runTests(solve)
  } catch (e) {
    return [{ name: '运行', ok: false, error: e?.message || String(e) }]
  }
}

/**
 * @param {'javascript'|'python'|'cpp'} language
 */
export async function runUserCodeAsync(code, problem, language) {
  if (language === 'cpp') {
    return [
      {
        name: '运行',
        ok: false,
        error:
          'C++ 无法在浏览器内编译运行。请切换到 JavaScript 或 Python，或在本地 IDE 中编写。',
      },
    ]
  }
  if (language === 'python') {
    return runPythonCode(code, problem)
  }
  return runUserCode(code, problem)
}
