<script setup lang="ts">
defineProps<{
  title: string
  detail: string
}>()
</script>

<template>
  <section class="upstream-state">
    <span class="badge">Fallback</span>
    <h3>{{ title }}</h3>
    <p>{{ detail }}</p>
  </section>
</template>

<style scoped>
.upstream-state {
  padding: 1.2rem;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(209, 77, 87, 0.08), rgba(255, 255, 255, 0.92));
  border: 1px solid rgba(209, 77, 87, 0.22);
}

.badge {
  display: inline-flex;
  margin-bottom: 0.8rem;
  padding: 0.3rem 0.55rem;
  border-radius: 999px;
  background: rgba(209, 77, 87, 0.12);
  color: var(--danger);
  font-size: 0.78rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
}

.upstream-state h3 {
  margin: 0 0 0.45rem;
  font-size: 1rem;
}

.upstream-state p {
  margin: 0;
  color: var(--muted);
}
</style>
