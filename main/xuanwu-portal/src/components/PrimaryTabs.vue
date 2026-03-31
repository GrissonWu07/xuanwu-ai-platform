<script setup lang="ts">
import { RouterLink } from 'vue-router'

import { primaryTabs } from '@/data/portal'
</script>

<template>
  <nav class="primary-tabs" aria-label="Primary navigation" role="tablist">
    <RouterLink
      v-for="tab in primaryTabs"
      :key="tab.label"
      :to="tab.to"
      custom
      v-slot="{ href, navigate, isActive }"
    >
      <a
        :href="href"
        role="tab"
        class="tab"
        :aria-selected="isActive"
        :data-active="isActive"
        @click="navigate"
      >
        {{ tab.label }}
      </a>
    </RouterLink>
  </nav>
</template>

<style scoped>
.primary-tabs {
  display: inline-flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.45rem;
  padding: 0.4rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(91, 109, 145, 0.16);
  box-shadow: var(--shadow-soft);
}

.tab {
  padding: 0.7rem 1rem;
  border-radius: 999px;
  color: var(--muted);
  font-weight: 600;
}

.tab[data-active='true'] {
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  color: white;
  box-shadow: 0 10px 20px rgba(91, 71, 245, 0.22);
}
</style>
