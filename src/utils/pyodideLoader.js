/** 浏览器端 Python：从 CDN 懒加载 Pyodide（首次约数 MB，需联网） */
const INDEX = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/'

let promise = null

export function loadPyodideOnce() {
  if (!promise) {
    promise = (async () => {
      const { loadPyodide } = await import(
        /* @vite-ignore */
        `${INDEX}pyodide.mjs`
      )
      return loadPyodide({ indexURL: INDEX })
    })()
  }
  return promise
}
