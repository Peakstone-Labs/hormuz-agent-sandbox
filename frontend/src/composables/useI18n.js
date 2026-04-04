import { ref, computed } from 'vue'

const locale = ref(localStorage.getItem('hormuz_locale') || 'en')
const strings = ref({})
const loaded = ref(false)

export function useI18n() {
  async function loadStrings(loc) {
    try {
      const res = await fetch(`/api/i18n?locale=${loc}`)
      const data = await res.json()
      strings.value = data.strings
      loaded.value = true
    } catch {
      loaded.value = false
    }
  }

  function setLocale(loc) {
    locale.value = loc
    localStorage.setItem('hormuz_locale', loc)
    loadStrings(loc)
  }

  function t(key, params = {}) {
    let s = strings.value[key] || key
    for (const [k, v] of Object.entries(params)) {
      s = s.replace(`{${k}}`, v)
    }
    return s
  }

  // Init
  if (!loaded.value) loadStrings(locale.value)

  return { locale, t, setLocale, loaded }
}
