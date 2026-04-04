<template>
  <div
    class="actor-card"
    :class="{ 'actor-card-expanded': expanded }"
    @click="expanded = !expanded"
  >
    <div class="card-header">
      <span style="font-size: 16px;">{{ emoji }}</span>
      <span class="card-sender">{{ sender }}</span>
      <span class="card-round">{{ t('round_label', { n: round }) }}</span>
    </div>

    <p class="card-action">{{ data.public_action }}</p>

    <div class="card-expand-hint">
      {{ expanded ? '▴' : '▾' }} {{ expanded ? 'COLLAPSE' : 'DETAILS' }}
    </div>

    <div v-if="expanded" class="card-detail space-y-2" @click.stop>
      <div>
        <div class="detail-label detail-label-strategy">{{ t('strategic_reasoning') }}</div>
        <p class="detail-text">{{ data.strategic_reasoning }}</p>
      </div>
      <div>
        <div class="detail-label detail-label-constraint">{{ t('constraints_considered') }}</div>
        <p class="detail-text">{{ data.constraints_considered }}</p>
      </div>
      <div>
        <div class="detail-label detail-label-risk">{{ t('risk_assessment') }}</div>
        <p class="detail-text">{{ data.risk_assessment }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from '../composables/useI18n'
const { t } = useI18n()

defineProps({
  sender: String,
  emoji: String,
  round: Number,
  data: Object,
})

const expanded = ref(false)
</script>
