import { ref } from 'vue'

const FREE_LIMIT = 20

function getOrCreateUUID() {
  let uuid = localStorage.getItem('hormuz_uuid')
  if (!uuid) {
    uuid = crypto.randomUUID()
    localStorage.setItem('hormuz_uuid', uuid)
  }
  return uuid
}

const clientUUID = getOrCreateUUID()
const usedCount = ref(parseInt(localStorage.getItem('hormuz_used') || '0', 10))

export function useTrial() {
  const remaining = ref(FREE_LIMIT - usedCount.value)

  function consume() {
    usedCount.value++
    localStorage.setItem('hormuz_used', String(usedCount.value))
    remaining.value = Math.max(0, FREE_LIMIT - usedCount.value)
  }

  function canTrial() {
    return remaining.value > 0
  }

  return { clientUUID, remaining, consume, canTrial }
}
