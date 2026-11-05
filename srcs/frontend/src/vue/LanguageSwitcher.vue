<script setup>
import { ref } from 'vue';
import { currentLang, setLanguage } from '../i18n';

const isOpen = ref(false);
const languages = [
  { code: 'en', label: 'EN' },
  { code: 'fr', label: 'FR' },
  { code: 'ar', label: 'AR' }
];

const selectLang = (code) => {
  setLanguage(code);
  isOpen.value = false;
};
</script>

<template>
  <div class="lang-switcher">
    <button class="lang-btn" @click="isOpen = !isOpen" title="Change Language">
      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
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
.lang-switcher { position: relative; display: flex; align-items: center; }
.lang-btn {
  display: flex; align-items: center; gap: 6px;
  background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
  color: white; padding: 6px 12px; border-radius: 12px; cursor: pointer;
  font-size: 0.8rem; transition: all 0.2s ease;
}
.lang-btn:hover { border-color: #00f2fe; color: #00f2fe; }
.lang-dropdown {
  position: absolute; top: 40px; right: 0;
  background: rgba(20, 10, 40, 0.95); border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px; padding: 6px; display: flex; flex-direction: column; gap: 4px;
  backdrop-filter: blur(16px); z-index: 100; min-width: 70px;
}
.lang-option {
  background: transparent; border: none; color: white; padding: 6px 10px;
  border-radius: 8px; cursor: pointer; text-align: center; font-size: 0.8rem;
}
.lang-option:hover, .lang-option.active {
  background: rgba(0, 242, 254, 0.2); color: #00f2fe;
}
</style>
