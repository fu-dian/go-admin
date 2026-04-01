import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAlgoContextStore = defineStore('algoContext', () => {
  const currentProblem = ref(null)

  function setCurrentProblem(p) {
    currentProblem.value = p
  }

  return { currentProblem, setCurrentProblem }
})
