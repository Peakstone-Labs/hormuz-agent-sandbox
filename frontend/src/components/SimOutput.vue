<template>
  <div class="flex flex-col min-h-0">
    <MarketBar
      :oilPrice="oilPrice"
      :initialPrice="initialPrice"
      :escalation="escalationIndex"
      :currentRound="currentRound"
      :totalRounds="totalRounds"
      :stepUnit="stepUnit"
    />

    <div ref="scrollContainer" class="flex-1 overflow-y-auto p-4 space-y-2" style="background: var(--color-bg-deep);">
      <template v-for="(group, roundNum) in groupedEvents" :key="roundNum">
        <div class="round-divider">{{ stepLabel }} {{ roundNum }}</div>

        <template v-for="(ev, i) in group" :key="i">
          <ActorCard
            v-if="ev.type === 'actor'"
            :sender="ev.sender"
            :emoji="actorEmoji(ev.sender)"
            :round="ev.round"
            :data="ev.data"
          />

          <div v-if="ev.type === 'market'" class="market-card">
            <div class="market-title">📊 {{ t('market_update') }}</div>
            <div class="market-price">{{ t('oil_price') }}: ${{ ev.data.oil_price?.toFixed(2) }}</div>
            <p class="market-commentary">{{ ev.data.commentary }}</p>
          </div>
        </template>
      </template>

      <!-- Loading -->
      <div v-if="status === 'running'" class="loading-terminal">
        <span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
        {{ t('loading') }}
      </div>

      <!-- Error -->
      <div v-if="status === 'error'" class="error-terminal">
        {{ errorMsg }}
      </div>

      <!-- Round complete -->
      <div v-if="status === 'round_done'" class="flex gap-3 justify-center flex-wrap pt-6 pb-4">
        <button v-if="currentRound < maxRounds" class="btn-next-terminal" @click="$emit('nextRound')">
          ▶ {{ stepLabel }} {{ currentRound + 1 }}
        </button>
        <button class="btn-report-action" @click="showReport = true">
          📊 {{ locale === 'zh' ? '生成报告' : 'Report' }}
        </button>
        <button class="btn-ghost-terminal" @click="$emit('restart')">
          ⟲ {{ t('rerun') }}
        </button>
      </div>
    </div>

    <!-- Report overlay -->
    <ReportCard
      v-if="showReport"
      :events="events"
      :oilPrice="oilPrice"
      :initialPrice="initialPrice"
      :escalation="escalationIndex"
      :chaosFactor="chaosFactor"
      :scenarioName="scenarioName"
      :stepUnit="stepUnit"
      :activeTagNames="activeTagNames"
      :actors="actors"
      @close="showReport = false"
    />
  </div>
</template>

<script setup>
import { computed, watch, ref, nextTick } from 'vue'
import { useI18n } from '../composables/useI18n'
import ActorCard from './ActorCard.vue'
import MarketBar from './MarketBar.vue'
import ReportCard from './ReportCard.vue'

const { t, locale } = useI18n()

const props = defineProps({
  events: Array,
  status: String,
  oilPrice: Number,
  initialPrice: Number,
  escalationIndex: Number,
  currentRound: Number,
  totalRounds: Number,
  stepUnit: String,
  errorMsg: String,
  actors: Object,
  chaosFactor: Number,
  scenarioName: String,
  activeTagNames: Array,
})
defineEmits(['nextRound', 'restart'])

const showReport = ref(false)
const maxRounds = 5

const scrollContainer = ref(null)

const groupedEvents = computed(() => {
  const groups = {}
  for (const ev of props.events) {
    if (ev.type === 'system' || ev.type === 'round_complete') continue
    const r = ev.round
    if (!groups[r]) groups[r] = []
    groups[r].push(ev)
  }
  return groups
})

const stepLabel = computed(() => {
  const map = { day: 'DAY', week: 'WEEK', month: 'MONTH' }
  return map[props.stepUnit] || 'ROUND'
})

function actorEmoji(sender) {
  return props.actors?.[sender]?.emoji || '🏛️'
}

watch(() => props.events.length, async () => {
  await nextTick()
  if (scrollContainer.value) {
    scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
  }
})
</script>
