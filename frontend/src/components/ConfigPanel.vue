<template>
  <div class="p-4 space-y-5">

    <!-- About blurb -->
    <div class="about-blurb">
      <p>{{ locale === 'zh'
        ? '基于多智能体（Multi-Agent）架构的地缘政治推演沙盒。每个国家由独立 AI 驱动，拥有各自的战略目标、约束条件和行为逻辑。调节参数，观察博弈如何涌现。'
        : 'A geopolitical sandbox powered by Multi-Agent AI. Each nation is driven by an independent LLM agent with its own strategic goals, constraints, and behavioral logic. Tune the parameters and watch the game theory emerge.'
      }}</p>
    </div>

    <!-- API Key + Model selector -->
    <div class="space-y-2">
      <div class="flex gap-2">
        <input
          type="password"
          class="input-terminal flex-1"
          :placeholder="t('api_key_placeholder')"
          v-model="config.apiKey"
        />
      </div>
      <div v-if="config.apiKey" class="flex gap-2 items-center">
        <span class="label-terminal shrink-0">MODEL</span>
        <select class="select-terminal flex-1" v-model="config.model">
          <optgroup label="Google Gemini">
            <option value="gemini/gemini-3-flash-preview">Gemini 3 Flash (fast, cheap)</option>
            <option value="gemini/gemini-2.5-pro-preview-05-06">Gemini 2.5 Pro (smart)</option>
          </optgroup>
          <optgroup label="OpenAI">
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4o-mini">GPT-4o Mini (fast, cheap)</option>
            <option value="o3-mini">o3-mini (reasoning)</option>
          </optgroup>
          <optgroup label="Anthropic">
            <option value="claude-sonnet-4-6">Claude Sonnet 4.6</option>
            <option value="claude-haiku-4-5-20251001">Claude Haiku 4.5 (fast)</option>
          </optgroup>
          <optgroup label="DeepSeek">
            <option value="deepseek/deepseek-v4-flash">DeepSeek V4 Flash (fast, cheap)</option>
            <option value="deepseek/deepseek-chat">DeepSeek V3 (cheap)</option>
            <option value="deepseek/deepseek-reasoner">DeepSeek R1 (reasoning)</option>
          </optgroup>
        </select>
      </div>
      <p v-if="config.apiKey" class="api-hint">
        {{ locale === 'zh'
          ? '密钥仅在内存中使用，不会被存储或记录。'
          : 'Your key is used in-memory only — never stored or logged.'
        }}
      </p>
    </div>

    <!-- Chaos Factor -->
    <div>
      <div class="flex items-center justify-between mb-1">
        <span class="label-terminal">{{ t('chaos_factor') }}</span>
        <span style="color: var(--color-neon-orange); font-size: 12px;">{{ config.chaosFactor.toFixed(1) }}</span>
      </div>
      <input
        type="range" min="0" max="1" step="0.1"
        class="slider-orange"
        v-model.number="config.chaosFactor"
      />
      <div class="flex justify-between mt-1" style="font-size: 10px; color: var(--color-text-muted);">
        <span>{{ t('chaos_low') }}</span>
        <span>{{ t('chaos_high') }}</span>
      </div>
    </div>

    <!-- Step Unit -->
    <div>
      <span class="label-terminal block mb-1">{{ t('step_unit') }}</span>
      <div class="flex gap-1">
        <button
          v-for="opt in [['day', t('step_day')], ['week', t('step_week')], ['month', t('step_month')]]"
          :key="opt[0]"
          class="step-btn"
          :class="{ active: config.stepUnit === opt[0] }"
          @click="config.stepUnit = opt[0]"
        >{{ opt[1] }}</button>
      </div>
    </div>

    <!-- Tags -->
    <TagPills
      :tags="tags"
      :selected="config.activeTags"
      @update:selected="config.activeTags = $event"
    />

    <!-- Actor Sliders -->
    <ActorSliders
      :actors="actors"
      :profiles="config.profiles"
      @update:profiles="config.profiles = $event"
    />

    <!-- Start Button -->
    <button
      class="btn-primary-terminal"
      :disabled="!canStart"
      @click="$emit('start')"
    >
      {{ t('start_simulation') }}
    </button>

    <!-- Trial info -->
    <p v-if="!config.apiKey" class="trial-info">
      {{ t('trial_remaining', { n: remaining }) }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useTrial } from '../composables/useTrial'
import TagPills from './TagPills.vue'
import ActorSliders from './ActorSliders.vue'

const { t, locale } = useI18n()
const { remaining, canTrial } = useTrial()

const props = defineProps({
  config: Object,
  tags: Object,
  actors: Object,
})
defineEmits(['start'])

const canStart = computed(() => {
  return props.config.apiKey || canTrial()
})
</script>
