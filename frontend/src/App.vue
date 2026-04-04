<template>
  <div class="min-h-screen flex flex-col">
    <!-- Nav -->
    <nav class="nav-terminal">
      <span class="nav-title flex items-center gap-2">
        <img src="/logo.png" alt="Peakstone Labs" class="nav-logo" />
        {{ t('app_title') }}
      </span>
      <div class="flex items-center gap-3">
        <a href="https://github.com/Peakstone-Labs/hormuz-agent-sandbox" target="_blank" class="github-link" title="GitHub">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
        </a>
        <button class="btn-locale" @click="setLocale(locale === 'en' ? 'zh' : 'en')">
          {{ locale === 'en' ? '中文' : 'EN' }}
        </button>
      </div>
    </nav>

    <!-- Main -->
    <div class="flex-1 flex flex-col md:flex-row overflow-hidden">
      <!-- Config sidebar -->
      <aside
        v-show="showConfig"
        class="sidebar-terminal w-full md:w-80 lg:w-96 shrink-0"
      >
        <div class="scenario-header">
          <h2>
            <span class="date-accent">{{ scenario.name }}</span>
          </h2>
          <div v-if="scenario.briefing?.length" class="briefing-lines">
            <p v-for="(line, i) in scenario.briefing" :key="i" class="briefing-line">
              <span class="briefing-bullet">›</span> {{ line }}
            </p>
          </div>
          <p v-else class="scenario-desc">{{ scenario.description }}</p>
        </div>

        <ConfigPanel
          :config="config"
          :tags="tags"
          :actors="actors"
          @start="handleStartRound1"
        />
      </aside>

      <!-- Output / Terminal viewport -->
      <main
        v-if="showOutput"
        class="flex-1 flex flex-col min-h-0 overflow-hidden scanline-overlay"
      >
        <SimOutput
          :events="events"
          :status="status"
          :oilPrice="oilPrice"
          :initialPrice="scenario.initial_oil_price"
          :escalationIndex="escalationIndex"
          :currentRound="currentRound"
          :totalRounds="99"
          :stepUnit="config.stepUnit"
          :errorMsg="errorMsg"
          :actors="actors"
          :chaosFactor="config.chaosFactor"
          :scenarioName="scenario.name"
          :activeTagNames="activeTagNames"
          @next-round="handleNextRound"
          @restart="handleRestart"
        />
      </main>

      <!-- Boot sequence terminal when idle (desktop only) -->
      <main
        v-if="!showOutput && !isMobile"
        class="flex-1 scanline-overlay"
        style="background: var(--color-bg-deep)"
      >
        <div class="boot-terminal">
          <p class="boot-line visible" style="animation-delay: 0s">$ hormuz-sim --version</p>
          <p class="boot-line visible" style="animation-delay: 0.3s">  v0.2.0 | Peakstone Labs</p>
          <p class="boot-line visible" style="animation-delay: 0.6s">&nbsp;</p>
          <p class="boot-line visible" style="animation-delay: 0.9s">$ cat /scenario/briefing.txt</p>
          <p class="boot-line visible" style="animation-delay: 1.2s">  [STRAIT OF HORMUZ] Status: BLOCKED</p>
          <p class="boot-line visible" style="animation-delay: 1.5s">  [OIL MARKET]       Brent: $110.00/bbl</p>
          <p class="boot-line visible" style="animation-delay: 1.8s">  [ESCALATION]       Index: 0.85 / 1.00</p>
          <p class="boot-line visible" style="animation-delay: 2.1s">  [ACTORS]           4 loaded</p>
          <p class="boot-line visible" style="animation-delay: 2.4s">  [TAGS]             11 available</p>
          <p class="boot-line visible" style="animation-delay: 2.7s">&nbsp;</p>
          <p class="boot-line visible" style="animation-delay: 3.0s">$ awaiting simulation parameters...<span class="boot-cursor"></span></p>
        </div>
      </main>
    </div>

    <!-- Footer -->
    <footer v-if="status === 'idle'" class="footer-terminal">
      {{ locale === 'zh' ? '由' : 'Powered by' }}
      <a href="https://www.peakstone-labs.com" target="_blank" class="footer-link">Peakstone Labs</a>
    </footer>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from './composables/useI18n'
import { useSimulation } from './composables/useSimulation'
import { useTrial } from './composables/useTrial'
import ConfigPanel from './components/ConfigPanel.vue'
import SimOutput from './components/SimOutput.vue'

const { locale, t, setLocale } = useI18n()
const { clientUUID, consume, canTrial } = useTrial()
const {
  status, events, currentRound, oilPrice, escalationIndex, errorMsg,
  runRound, stop, reset,
} = useSimulation()

const scenario = ref({ name: '', description: '', initial_oil_price: 110 })
const actors = ref({})
const tags = ref({})

const config = reactive({
  apiKey: '',
  chaosFactor: 0.5,
  stepUnit: 'day',
  model: 'gemini/gemini-3-flash-preview',
  activeTags: [],
  profiles: {},
})

const isMobile = ref(window.innerWidth < 768)
window.addEventListener('resize', () => { isMobile.value = window.innerWidth < 768 })

const activeTagNames = computed(() => {
  return config.activeTags
    .filter(id => tags.value[id])
    .map(id => `${tags.value[id].emoji} ${tags.value[id].name}`)
})

const showConfig = computed(() => {
  if (!isMobile.value) return true
  return status.value === 'idle'
})

const showOutput = computed(() => {
  return status.value !== 'idle'
})

onMounted(async () => {
  try {
    const res = await fetch(`/api/presets?locale=${locale.value}`)
    const data = await res.json()
    scenario.value = data.scenario
    actors.value = data.actors
    tags.value = data.tags
  } catch (e) {
    console.error('Failed to load presets:', e)
  }
})

function buildPayload() {
  return {
    client_uuid: clientUUID,
    api_key: config.apiKey || undefined,
    chaos_factor: config.chaosFactor,
    step_unit: config.stepUnit,
    active_tags: config.activeTags,
    profiles: config.profiles,
    model: config.apiKey ? config.model : undefined,
    locale: locale.value,
  }
}

async function handleStartRound1() {
  if (!config.apiKey && !canTrial()) return
  if (!config.apiKey) consume()
  reset()
  await runRound(buildPayload(), 1)
}

async function handleNextRound() {
  await runRound(buildPayload(), currentRound.value + 1)
}

function handleRestart() {
  reset()
}
</script>
