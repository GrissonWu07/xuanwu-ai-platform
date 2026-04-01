<script setup lang="ts">
defineProps<{
  title: string
  chips: string[]
}>()
</script>

<template>
  <section class="toolbar" :aria-label="title">
    <label class="search">
      <span aria-hidden="true">⌕</span>
      <input type="search" :placeholder="title" />
    </label>
    <div class="chips">
      <button v-for="chip in chips" :key="chip" type="button" class="chip">{{ chip }}</button>
    </div>
  </section>
</template>

<style scoped>
.toolbar {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) auto;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(91, 109, 145, 0.14);
  box-shadow: var(--shadow-soft);
}

.search {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem 0.95rem;
  border-radius: 16px;
  background: rgba(124, 108, 255, 0.06);
}

.search span {
  color: var(--soft);
}

.search input {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  align-items: center;
}

.chip {
  min-height: 2.5rem;
  padding: 0 0.9rem;
  border-radius: 999px;
  background: rgba(124, 108, 255, 0.1);
  color: var(--accent-strong);
  font-weight: 600;
}

@media (max-width: 820px) {
  .toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
