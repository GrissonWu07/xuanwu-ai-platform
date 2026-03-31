<script setup lang="ts">
defineProps<{
  title: string
  detail: string
}>()
</script>

<template>
  <section class="empty-state">
    <h3>{{ title }}</h3>
    <p>{{ detail }}</p>
  </section>
</template>

<style scoped>
.empty-state {
  padding: 1.2rem;
  border-radius: 22px;
  background: rgba(124, 108, 255, 0.08);
  border: 1px dashed rgba(124, 108, 255, 0.24);
}

.empty-state h3 {
  margin: 0 0 0.4rem;
  font-size: 1rem;
}

.empty-state p {
  margin: 0;
  color: var(--muted);
}
</style>
