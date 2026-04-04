<template>
  <div class="report-overlay" @click.self="$emit('close')">
    <div class="report-wrapper">
      <!-- The card that gets captured as image -->
      <div ref="cardRef" class="report-card">
        <!-- Header -->
        <div class="report-header">
          <img src="/logo.png" alt="Peakstone Labs" class="report-logo" />
          <div class="flex-1">
            <div class="report-title">HORMUZ STRAIT SIMULATOR</div>
            <div class="report-subtitle">{{ scenarioName }}</div>
          </div>
          <img v-if="qrDataUrl" :src="qrDataUrl" alt="Scan to play" class="report-qr" />
        </div>

        <!-- Stats row -->
        <div class="report-stats">
          <div class="stat-box">
            <div class="stat-label">ROUNDS</div>
            <div class="stat-value">{{ totalRounds }}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">OIL PRICE</div>
            <div class="stat-value" :class="oilChange > 0 ? 'stat-up' : 'stat-down'">
              ${{ oilPrice?.toFixed(0) }}
              <span class="stat-change">{{ oilChange > 0 ? '↑' : '↓' }}{{ Math.abs(oilChange).toFixed(0) }}%</span>
            </div>
          </div>
          <div class="stat-box">
            <div class="stat-label">ESCALATION</div>
            <div class="stat-value" :class="escClass">{{ escalation?.toFixed(2) }}</div>
          </div>
          <div class="stat-box">
            <div class="stat-label">CHAOS</div>
            <div class="stat-value">{{ chaosFactor?.toFixed(1) }}</div>
          </div>
        </div>

        <!-- Active tags -->
        <div v-if="activeTags.length" class="report-tags">
          <span v-for="tag in activeTags" :key="tag" class="report-tag">{{ tag }}</span>
        </div>

        <!-- Timeline -->
        <div class="report-timeline">
          <div v-for="(round, i) in timeline" :key="i" class="timeline-round">
            <div class="timeline-header">
              <span class="timeline-round-label">{{ round.label }}</span>
              <span class="timeline-oil">${{ round.oilPrice?.toFixed(0) }}</span>
            </div>
            <div v-for="action in round.actions" :key="action.sender" class="timeline-action">
              <span class="timeline-actor">{{ action.emoji }} {{ action.sender }}</span>
              <span class="timeline-text">{{ truncate(action.text, 100) }}</span>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="report-footer">
          <span>peakstone-labs.com</span>
          <span class="report-date">{{ new Date().toISOString().split('T')[0] }}</span>
        </div>
      </div>

      <!-- Action buttons (outside the captured area) -->
      <div class="report-actions">
        <button class="btn-report-action" @click="downloadImage">
          📥 {{ locale === 'zh' ? '下载图片' : 'Download Image' }}
        </button>
        <button class="btn-report-action" @click="copyText">
          📋 {{ locale === 'zh' ? '复制文字' : 'Copy Text' }}
        </button>
        <button class="btn-report-close" @click="$emit('close')">
          ✕ {{ locale === 'zh' ? '关闭' : 'Close' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import html2canvas from 'html2canvas-pro'
import QRCode from 'qrcode'
import { useI18n } from '../composables/useI18n'

const { locale } = useI18n()

const GAME_URL = 'https://www.peakstone-labs.com/hormuz_simulator'
const qrDataUrl = ref(null)

onMounted(async () => {
  qrDataUrl.value = await QRCode.toDataURL(GAME_URL, {
    width: 80,
    margin: 1,
    color: { dark: '#e5e5ec', light: '#00000000' },
  })
})

const props = defineProps({
  events: Array,
  oilPrice: Number,
  initialPrice: Number,
  escalation: Number,
  chaosFactor: Number,
  scenarioName: String,
  stepUnit: String,
  activeTagNames: Array,
  actors: Object,
})
defineEmits(['close'])

const cardRef = ref(null)

const totalRounds = computed(() => {
  const rounds = props.events.filter(e => e.type === 'market').map(e => e.round)
  return rounds.length ? Math.max(...rounds) : 0
})

const oilChange = computed(() => {
  if (!props.initialPrice || !props.oilPrice) return 0
  return ((props.oilPrice - props.initialPrice) / props.initialPrice) * 100
})

const escClass = computed(() => {
  if (!props.escalation) return ''
  if (props.escalation > 0.8) return 'stat-up'
  if (props.escalation > 0.5) return 'stat-warn'
  return 'stat-down'
})

const activeTags = computed(() => props.activeTagNames || [])

const stepLabel = computed(() => {
  const map = { day: 'DAY', week: 'WEEK', month: 'MONTH' }
  return map[props.stepUnit] || 'ROUND'
})

const timeline = computed(() => {
  const rounds = {}
  for (const ev of props.events) {
    if (ev.type !== 'actor' && ev.type !== 'market') continue
    if (!rounds[ev.round]) rounds[ev.round] = { label: `${stepLabel.value} ${ev.round}`, actions: [], oilPrice: null }
    if (ev.type === 'actor') {
      rounds[ev.round].actions.push({
        sender: ev.sender,
        emoji: props.actors?.[ev.sender]?.emoji || '🏛️',
        text: ev.data.public_action,
      })
    }
    if (ev.type === 'market') {
      rounds[ev.round].oilPrice = ev.data.oil_price
    }
  }
  return Object.values(rounds)
})

function truncate(text, max) {
  if (!text || text.length <= max) return text
  return text.slice(0, max) + '...'
}

async function downloadImage() {
  if (!cardRef.value) return
  const canvas = await html2canvas(cardRef.value, {
    backgroundColor: '#0a0a0f',
    scale: 2,
  })
  const link = document.createElement('a')
  link.download = `hormuz-sim-report-${Date.now()}.png`
  link.href = canvas.toDataURL('image/png')
  link.click()
}

function copyText() {
  const lines = [`HORMUZ STRAIT SIMULATOR - ${props.scenarioName}`, '']
  lines.push(`Oil: $${props.initialPrice} → $${props.oilPrice?.toFixed(0)} (${oilChange.value > 0 ? '+' : ''}${oilChange.value.toFixed(0)}%)`)
  lines.push(`Escalation: ${props.escalation?.toFixed(2)}`)
  lines.push(`Chaos: ${props.chaosFactor?.toFixed(1)}`)
  if (activeTags.value.length) lines.push(`Tags: ${activeTags.value.join(', ')}`)
  lines.push('')

  for (const round of timeline.value) {
    lines.push(`--- ${round.label} --- Oil: $${round.oilPrice?.toFixed(0)}`)
    for (const a of round.actions) {
      lines.push(`${a.emoji} ${a.sender}: ${a.text}`)
    }
    lines.push('')
  }

  lines.push('peakstone-labs.com')
  navigator.clipboard.writeText(lines.join('\n'))
}
</script>
