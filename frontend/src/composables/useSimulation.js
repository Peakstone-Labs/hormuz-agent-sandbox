import { ref } from 'vue'

export function useSimulation() {
  const status = ref('idle') // idle | running | round_done | error
  const events = ref([])
  const currentRound = ref(0)
  const oilPrice = ref(null)
  const escalationIndex = ref(null)
  const errorMsg = ref('')
  // State carried between rounds
  const summaries = ref([])
  let abortController = null

  async function runRound(config, roundNum) {
    status.value = 'running'
    errorMsg.value = ''
    currentRound.value = roundNum

    abortController = new AbortController()

    const payload = {
      ...config,
      round_num: roundNum,
      previous_summaries: summaries.value,
      previous_oil_price: oilPrice.value,
    }

    try {
      const res = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: abortController.signal,
      })

      if (!res.ok) {
        const err = await res.json()
        errorMsg.value = err.detail?.message || err.detail || 'Request failed'
        status.value = 'error'
        return
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop()

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          try {
            const event = JSON.parse(line.slice(6))
            events.value.push(event)

            if (event.type === 'market') {
              oilPrice.value = event.data.oil_price
              escalationIndex.value = event.data.escalation_index
            }
            if (event.type === 'round_complete') {
              // Save state for next round
              oilPrice.value = event.data.oil_price
              summaries.value = event.data.summaries
              status.value = 'round_done'
            }
            if (event.type === 'error') {
              errorMsg.value = event.data.message
              status.value = 'error'
            }
          } catch { /* skip malformed */ }
        }
      }

      if (status.value === 'running') status.value = 'round_done'
    } catch (e) {
      if (e.name !== 'AbortError') {
        errorMsg.value = e.message
        status.value = 'error'
      }
    }
  }

  function stop() {
    if (abortController) abortController.abort()
    status.value = 'idle'
  }

  function reset() {
    stop()
    events.value = []
    currentRound.value = 0
    oilPrice.value = null
    escalationIndex.value = null
    errorMsg.value = ''
    summaries.value = []
    status.value = 'idle'
  }

  return {
    status, events, currentRound, oilPrice, escalationIndex, errorMsg,
    runRound, stop, reset,
  }
}
