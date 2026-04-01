<script setup lang="ts">
import { RouterLink } from 'vue-router'

defineProps<{
  title: string
  value: string
  detail: string
  tone?: 'accent' | 'blue' | 'green' | 'amber'
  to?: string
}>()
</script>

<template>
  <component
    :is="to ? RouterLink : 'article'"
    class="summary-card"
    :class="{ 'summary-card--interactive': Boolean(to) }"
    :data-tone="tone ?? 'accent'"
    :to="to"
  >
    <p class="summary-title">{{ title }}</p>
    <div class="summary-value">{{ value }}</div>
    <p class="summary-detail">{{ detail }}</p>
  </component>
</template>

<style scoped>
.summary-card {
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 1.2rem 1.2rem 1.35rem;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}

.summary-card--interactive {
  display: block;
  color: inherit;
  transition:
    transform 160ms ease,
    box-shadow 160ms ease,
    border-color 160ms ease;
}

.summary-card--interactive:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow);
  border-color: rgba(124, 108, 255, 0.24);
}

.summary-card::before {
  content: '';
  position: absolute;
  inset: auto -20% -40% auto;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(124, 108, 255, 0.18), transparent 66%);
}

.summary-card[data-tone='blue']::before {
  background: radial-gradient(circle, rgba(84, 156, 255, 0.16), transparent 66%);
}

.summary-card[data-tone='green']::before {
  background: radial-gradient(circle, rgba(29, 154, 116, 0.16), transparent 66%);
}

.summary-card[data-tone='amber']::before {
  background: radial-gradient(circle, rgba(185, 132, 20, 0.18), transparent 66%);
}

.summary-title {
  margin: 0 0 0.35rem;
  color: var(--muted);
  font-size: 0.88rem;
}

.summary-value {
  position: relative;
  font-size: 2rem;
  line-height: 1.05;
  font-weight: 700;
  letter-spacing: -0.04em;
}

.summary-detail {
  position: relative;
  margin: 0.55rem 0 0;
  color: var(--soft);
  font-size: 0.93rem;
}
</style>
