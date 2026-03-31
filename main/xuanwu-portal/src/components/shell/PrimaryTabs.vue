<template>
  <nav class="primary-tabs" aria-label="Primary navigation" role="tablist">
    <RouterLink
      v-for="tab in tabs"
      :key="tab.to"
      :to="tab.to"
      class="primary-tabs__link"
      custom
      v-slot="{ navigate, href, isActive }"
    >
      <button
        :aria-selected="isActive"
        :class="['primary-tabs__button', { 'primary-tabs__button--active': isActive }]"
        :href="href"
        role="tab"
        type="button"
        @click="navigate"
      >
        {{ tab.label }}
      </button>
    </RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

const tabs = [
  { label: 'Overview', to: '/overview' },
  { label: 'Devices', to: '/devices' },
  { label: 'Agents', to: '/agents' },
  { label: 'Jobs', to: '/jobs' },
  { label: 'Alerts', to: '/alerts' },
]
</script>
