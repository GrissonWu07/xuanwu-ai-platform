<template>
  <div class="portal-shell">
    <header class="portal-topbar">
      <div class="portal-brand">
        <span class="portal-brand__eyebrow">Xuanwu AI</span>
        <span class="portal-brand__name">Portal</span>
      </div>
      <div class="portal-search">
        <input aria-label="Search portal" placeholder="Search devices, agents, jobs" />
      </div>
      <div class="portal-topbar__meta">
        <span class="status-pill">248 devices</span>
        <span class="status-pill">12 active jobs</span>
        <ProfileMenu />
      </div>
    </header>

    <PrimaryTabs />

    <main class="portal-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'

import PrimaryTabs from '@/components/shell/PrimaryTabs.vue'
import ProfileMenu from '@/components/shell/ProfileMenu.vue'
</script>
