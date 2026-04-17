<template>
  <div>
    <span class="label-terminal block mb-2">{{ t('actors_panel') }}</span>
    <div class="space-y-1.5">
      <details
        v-for="(actor, id) in actors"
        :key="id"
        class="actor-panel"
      >
        <summary class="actor-summary">
          <span class="actor-icon">{{ actor.emoji }}</span>
          <span class="actor-name">{{ actor.short_name || actor.display_name }}</span>
          <span class="actor-chevron">▼</span>
        </summary>
        <div class="px-3 pb-3 space-y-3">
          <p class="actor-desc">{{ actor.description }}</p>

          <!-- Main sliders -->
          <div>
            <div class="slider-row">
              <span class="slider-label-main">{{ t('aggressiveness') }}</span>
              <span class="slider-val-main" style="color: var(--color-neon-blue);">{{ profileFor(id).aggressiveness.toFixed(1) }}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.1"
              class="slider-blue"
              :value="profileFor(id).aggressiveness"
              @input="setField(id, 'aggressiveness', $event)"
            />
          </div>

          <div>
            <div class="slider-row">
              <span class="slider-label-main">{{ t('economic_tolerance') }}</span>
              <span class="slider-val-main" style="color: var(--color-neon-red);">{{ profileFor(id).economic_tolerance.toFixed(1) }}</span>
            </div>
            <input
              type="range" min="0" max="1" step="0.1"
              class="slider-red"
              :value="profileFor(id).economic_tolerance"
              @input="setField(id, 'economic_tolerance', $event)"
            />
          </div>

          <!-- Advanced: constraints (collapsed by default) -->
          <details v-if="actor.default_profile?.constraints" class="advanced-panel">
            <summary class="advanced-toggle">
              ⚙ {{ locale === 'zh' ? '高级约束设定' : 'ADVANCED CONSTRAINTS' }}
              <span class="advanced-count">{{ Object.keys(actor.default_profile.constraints).length }}</span>
            </summary>
            <div class="pt-2 space-y-2">
              <div v-for="(val, cKey) in actor.default_profile.constraints" :key="cKey">
                <div class="slider-row">
                  <span class="constraint-label flex items-center gap-1">
                    {{ constraintLabel(id, cKey) }}
                    <button class="info-btn" @click.prevent="toggleTip(id, cKey)">ⓘ</button>
                  </span>
                  <span class="constraint-val">{{ constraintVal(id, cKey, val).toFixed(1) }}</span>
                </div>
                <p v-if="openTip === id + ':' + cKey" class="constraint-tip">
                  {{ constraintTip(id, cKey) }}
                </p>
                <input
                  type="range" min="0" max="1" step="0.1"
                  class="slider-dim"
                  :value="constraintVal(id, cKey, val)"
                  @input="setConstraint(id, cKey, $event)"
                />
              </div>
            </div>
          </details>
        </div>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from '../composables/useI18n'
const { t, locale } = useI18n()

const openTip = ref(null)
function toggleTip(id, key) {
  const k = id + ':' + key
  openTip.value = openTip.value === k ? null : k
}

const props = defineProps({
  actors: Object,
  profiles: Object,
})
const emit = defineEmits(['update:profiles'])

function profileFor(id) {
  if (props.profiles[id]) return props.profiles[id]
  const d = props.actors[id]?.default_profile || {}
  return {
    aggressiveness: d.aggressiveness ?? 0.5,
    economic_tolerance: d.economic_tolerance ?? 0.5,
    red_lines: d.red_lines || [],
    constraints: { ...(d.constraints || {}) },
  }
}

function setField(id, field, event) {
  const p = { ...profileFor(id) }
  p[field] = parseFloat(event.target.value)
  emit('update:profiles', { ...props.profiles, [id]: p })
}

function constraintVal(id, key, fallback) {
  return profileFor(id).constraints?.[key] ?? fallback
}

function setConstraint(id, key, event) {
  const p = { ...profileFor(id) }
  p.constraints = { ...(p.constraints || {}) }
  p.constraints[key] = parseFloat(event.target.value)
  emit('update:profiles', { ...props.profiles, [id]: p })
}

function constraintLabel(actorId, key) {
  const actor = props.actors[actorId]
  if (actor?.constraints_labels?.[key]) return actor.constraints_labels[key]
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

const CONSTRAINT_TIPS = {
  missile_stockpile: { en: '0=depleted, 1=full arsenal. Low → relies on proxies/mines', zh: '0=耗尽, 1=满库存。低值→依赖代理人/水雷' },
  nuclear_proximity: { en: '0=far from weapons-grade, 1=near breakout', zh: '0=远离武器级, 1=接近突破' },
  infrastructure_resilience: { en: '0=fragile, 1=hardened. Low → vulnerable to strikes', zh: '0=脆弱, 1=坚固。低值→难以承受打击' },
  proxy_coordination: { en: '0=no control, 1=full. High → can activate Houthis', zh: '0=无法指挥, 1=完全协调。高值→可激活胡塞' },
  succession_stability: { en: '0=unstable, 1=consolidated', zh: '0=不稳定, 1=已巩固' },
  force_readiness: { en: '0=not ready, 1=fully deployed', zh: '0=未就绪, 1=全面部署' },
  domestic_tolerance: { en: '0=no patience, 1=strong support', zh: '0=零容忍, 1=强力支持' },
  coalition_cohesion: { en: '0=isolated, 1=united', zh: '0=孤立, 1=团结' },
  escalation_commitment: { en: '0=seeking off-ramp, 1=hard victory', zh: '0=寻找退路, 1=决心困难胜利' },
  fiscal_capacity: { en: '0=strained, 1=ample', zh: '0=紧张, 1=充裕' },
  strategic_depth: { en: 'Fixed low — no geographic buffer', zh: '固定低值——缺乏地理缓冲' },
  us_dependency: { en: '0=independent, 1=fully dependent', zh: '0=独立, 1=完全依赖' },
  northern_front_risk: { en: '0=safe, 1=imminent threat', zh: '0=安全, 1=迫在眉睫' },
  escalation_urgency: { en: '0=patient, 1=now or never', zh: '0=耐心, 1=现在或永远' },
  international_legitimacy: { en: '0=isolated, 1=supported', zh: '0=孤立, 1=受支持' },
  oil_leverage: { en: '3M bbl/day spare = your only card', zh: '300万桶/日备用=唯一的牌' },
  infrastructure_vulnerability: { en: 'Desalination serves millions', zh: '海水淡化厂服务数百万人' },
  agency: { en: 'Structurally very low — reactive only', zh: '结构性极低——只能被动应对' },
  houthi_exposure: { en: 'Yanbu corridor = economic oxygen', zh: '延布走廊=经济氧气' },
  capital_flight_risk: { en: 'War drives capital to US/Europe', zh: '战争驱动资本外逃' },
}

function constraintTip(actorId, key) {
  const labels = props.actors[actorId]?.constraints_labels || {}
  const isChinese = Object.values(labels).some(v => /[\u4e00-\u9fff]/.test(v))
  const lang = isChinese ? 'zh' : 'en'
  return CONSTRAINT_TIPS[key]?.[lang] || CONSTRAINT_TIPS[key]?.en || key
}
</script>
