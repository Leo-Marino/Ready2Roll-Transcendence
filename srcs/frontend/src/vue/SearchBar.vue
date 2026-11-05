<script setup>
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const props = defineProps({ placeholder: { type: String, default: 'Search...' } });

const router = useRouter();
const route = useRoute();

const text = ref(route.name === 'search' ? String(route.query.q || '') : '');
watch(() => route.query.q, (q) => {
  if (route.name === 'search') text.value = String(q || '');
});

const go = () => {
  const q = text.value.trim();
  if (!q) return;
  router.push({ name: 'search', query: { q } });
};
</script>

<template>
  <form class="search-bar" @submit.prevent="go">
    <input v-model="text" type="text" :placeholder="placeholder" maxlength="50" autocomplete="off">
  </form>
</template>

<style scoped>
.search-bar {
  flex: 1;
  max-width: 300px;
  margin: 0 10px;
}

.search-bar input {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 17px;
  padding: 10px 20px;
  color: white;
  width: 100%;
  box-sizing: border-box;
  outline: none;
  transition: background 0.2s ease;
}

.search-bar input:focus {
  background: rgba(255, 255, 255, 0.18);
}

@media (max-width: 600px) {
  .search-bar {
    max-width: 150px;
  }
  .search-bar input {
    padding: 8px 12px;
    font-size: 0.85rem;
  }
}
</style>
