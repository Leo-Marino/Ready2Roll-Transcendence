<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { currentLang, setLanguage } from '../i18n';

const isOpen = ref(false);
const rootRef = ref(null);

const languages = [
  { code: 'en', label: 'English (EN)' },
  { code: 'fr', label: 'Français (FR)' },
  { code: 'ar', label: 'العربية (AR)' }
];

const selectLang = (code) => {
  setLanguage(code);
  isOpen.value = false;
};

const handleClickOutside = (e) => {
  if (isOpen.value && rootRef.value && !rootRef.value.contains(e.target)) {
    isOpen.value = false;
  }
};

onMounted(() => document.addEventListener('click', handleClickOutside));
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside));
</script>

<template>
  <div class="lang-switcher" ref="rootRef">
    <button class="lang-btn" @click="isOpen = !isOpen" title="Change Language">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="globe-icon">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/>
        <path d="M2 12h20"/>
      </svg>
      <span>{{ currentLang.toUpperCase() }}</span>
    </button>

    <div v-if="isOpen" class="lang-dropdown">
      <button
        v-for="l in languages"
        :key="l.code"
        class="lang-option"
        :class="{ active: currentLang === l.code }"
        @click="selectLang(l.code)"
      >
        {{ l.label }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.lang-switcher {
  position: relative;
  display: flex;
  align-items: center;
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #ffffff;
  padding: 6px 12px;
  border-radius: 12px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.lang-btn:hover {
  border-color: #00f2fe;
  color: #00f2fe;
}

.lang-dropdown {
  position: absolute;
  top: 42px;
  right: 0;
  background: rgba(20, 10, 40, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  backdrop-filter: blur(16px);
  z-index: 1000;
  min-width: 130px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.lang-option {
  background: transparent;
  border: none;
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  font-size: 0.82rem;
  transition: background 0.2s ease, color 0.2s ease;
}

.lang-option:hover,
.lang-option.active {
  background: rgba(0, 242, 254, 0.2);
  color: #00f2fe;
}

[dir="rtl"] .lang-dropdown {
  right: auto;
  left: 0;
}

</style>
