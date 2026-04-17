<template>
  <div v-if="open" class="bg-modal-backdrop" @click.self="$emit('close')">
    <div class="bg-modal">
      <div class="bg-modal-header">
        <div class="bg-modal-tabs">
          <button
            class="bg-modal-tab"
            :class="{ active: activeTab === 'en' }"
            @click="activeTab = 'en'"
          >EN</button>
          <button
            class="bg-modal-tab"
            :class="{ active: activeTab === 'zh' }"
            @click="activeTab = 'zh'"
          >中文</button>
        </div>
        <button class="bg-modal-close" @click="$emit('close')" title="Close">✕</button>
      </div>
      <div class="bg-modal-body markdown-body" v-html="renderedHtml"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  open: Boolean,
  content: { type: Object, default: () => ({ en: '', zh: '' }) },
  initialLocale: { type: String, default: 'en' },
})

defineEmits(['close'])

const activeTab = ref(props.initialLocale === 'zh' ? 'zh' : 'en')

watch(() => props.open, (val) => {
  if (val) activeTab.value = props.initialLocale === 'zh' ? 'zh' : 'en'
})

const renderedHtml = computed(() => {
  const md = props.content[activeTab.value] || ''
  return marked.parse(md, { breaks: true, gfm: true })
})
</script>
