<template>
  <div>
    <span class="label-terminal block mb-3">{{ t('tags_panel') }}</span>

    <div v-for="(group, cat) in groupedTags" :key="cat" class="mb-3">
      <div class="tag-category-header" :style="{ color: catColor(cat) }">
        {{ catLabel(cat) }}
      </div>
      <div class="flex flex-wrap gap-1.5 mt-1">
        <button
          v-for="[id, tag] in group"
          :key="id"
          class="tag-pill"
          :class="selected.includes(id) ? 'active-' + tag.category : ''"
          @click="toggle(id)"
        >
          {{ tag.emoji }} {{ tag.name }}
        </button>
      </div>
    </div>

    <!-- Descriptions of selected tags -->
    <div v-if="selectedDescs.length" class="mt-2 space-y-1 tag-desc-block">
      <p v-for="item in selectedDescs" :key="item.id">
        {{ item.emoji }} {{ item.desc }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
const { t } = useI18n()

const props = defineProps({
  tags: Object,
  selected: Array,
})
const emit = defineEmits(['update:selected'])

const CATEGORY_ORDER = ['military', 'escalation', 'diplomacy', 'economic', 'political']
const CAT_COLORS = {
  military: 'var(--color-neon-red)',
  escalation: 'var(--color-neon-orange)',
  diplomacy: 'var(--color-neon-blue)',
  economic: 'var(--color-neon-green)',
  political: '#a78bfa',
}

const groupedTags = computed(() => {
  const groups = {}
  for (const [id, tag] of Object.entries(props.tags || {})) {
    const cat = tag.category || 'misc'
    if (!groups[cat]) groups[cat] = []
    groups[cat].push([id, tag])
  }
  // Sort by defined order
  const sorted = {}
  for (const cat of CATEGORY_ORDER) {
    if (groups[cat]) sorted[cat] = groups[cat]
  }
  // Add any remaining
  for (const cat of Object.keys(groups)) {
    if (!sorted[cat]) sorted[cat] = groups[cat]
  }
  return sorted
})

function toggle(id) {
  const s = [...props.selected]
  const i = s.indexOf(id)
  if (i >= 0) s.splice(i, 1)
  else s.push(id)
  emit('update:selected', s)
}

const selectedDescs = computed(() => {
  return props.selected
    .filter(id => props.tags[id])
    .map(id => ({ id, emoji: props.tags[id].emoji, desc: props.tags[id].description }))
})

function catColor(cat) { return CAT_COLORS[cat] || '#6b6b7b' }

function catLabel(cat) {
  return t('category_' + cat) || cat.toUpperCase()
}
</script>
