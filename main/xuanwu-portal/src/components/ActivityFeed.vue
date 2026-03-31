<script setup lang="ts">
defineProps<{
  items: Array<{ title: string; meta: string }>
}>()
</script>

<template>
  <div class="feed">
    <div v-for="item in items" :key="item.title" class="feed-item">
      <span class="feed-dot" aria-hidden="true" />
      <div>
        <p>{{ item.title }}</p>
        <span>{{ item.meta }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.feed {
  display: grid;
  gap: 0.9rem;
}

.feed-item {
  display: grid;
  grid-template-columns: 0.8rem 1fr;
  gap: 0.8rem;
  align-items: start;
}

.feed-dot {
  margin-top: 0.45rem;
  width: 0.7rem;
  height: 0.7rem;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  box-shadow: 0 0 0 6px rgba(124, 108, 255, 0.12);
}

.feed-item p {
  margin: 0;
  font-weight: 600;
}

.feed-item span {
  color: var(--soft);
  font-size: 0.92rem;
}
</style>
