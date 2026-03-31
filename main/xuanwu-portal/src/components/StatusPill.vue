<script setup lang="ts">
defineProps<{
  label: string
  value: string
}>()
</script>

<template>
  <span class="status-pill">
    <strong>{{ value }}</strong>
    <span>{{ label }}</span>
  </span>
</template>

<style scoped>
.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(124, 108, 255, 0.16);
  box-shadow: var(--shadow-soft);
  color: var(--muted);
  white-space: nowrap;
}

.status-pill strong {
  color: var(--text);
  font-size: 0.95rem;
}

.status-pill span {
  font-size: 0.86rem;
}
</style>
