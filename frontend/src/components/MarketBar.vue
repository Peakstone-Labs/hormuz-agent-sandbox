<template>
  <div v-if="oilPrice != null" class="market-bar">
    <div class="flex items-center gap-3">
      <span class="oil-price" :class="priceColor">
        🛢️ ${{ oilPrice.toFixed(2) }}
      </span>
      <span v-if="change != null" :class="priceColor" style="font-size: 11px;">
        {{ change > 0 ? '↑' : '↓' }}{{ Math.abs(change).toFixed(1) }}%
      </span>
    </div>
    <div class="flex items-center gap-2">
      <span style="font-size: 10px; color: var(--color-text-muted);">ESC</span>
      <span class="esc-bar">
        <span
          class="esc-fill"
          :class="escColor"
          :style="{ width: (escalation * 100) + '%' }"
        ></span>
      </span>
      <span style="font-size: 11px; color: var(--color-text-muted); font-variant-numeric: tabular-nums;">{{ escalation?.toFixed(2) }}</span>
    </div>
    <span class="round-badge">
      {{ stepLabel }} {{ currentRound }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  oilPrice: Number,
  initialPrice: Number,
  escalation: Number,
  currentRound: Number,
  totalRounds: Number,
  stepUnit: String,
})

const change = computed(() => {
  if (!props.initialPrice || !props.oilPrice) return null
  return ((props.oilPrice - props.initialPrice) / props.initialPrice) * 100
})

const priceColor = computed(() => {
  if (change.value == null) return ''
  return change.value > 0 ? 'oil-up' : 'oil-down'
})

const escColor = computed(() => {
  if (!props.escalation) return 'esc-low'
  if (props.escalation > 0.8) return 'esc-high'
  if (props.escalation > 0.5) return 'esc-mid'
  return 'esc-low'
})

const stepLabel = computed(() => {
  const map = { day: 'DAY', week: 'WEEK', month: 'MONTH' }
  return map[props.stepUnit] || 'ROUND'
})
</script>
