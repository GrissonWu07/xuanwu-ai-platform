<template>
  <div class="profile-menu">
    <button
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="menu"
      class="profile-menu__trigger"
      type="button"
      @click="open = !open"
    >
      <span class="profile-menu__avatar">GW</span>
      <span class="profile-menu__meta">
        <strong>Gang Wu</strong>
        <small>Platform owner</small>
      </span>
    </button>
    <div v-if="open" class="profile-menu__content" role="menu">
      <button
        v-for="item in menuItems"
        :key="item"
        role="menuitem"
        type="button"
        @click="open = false"
      >
        {{ item }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const open = ref(false)
const menuItems = [
  'Users & Roles',
  'Channels & Gateways',
  'AI Config Proxy',
  'Telemetry & Alarms',
  'Settings',
  'Sign out',
]
</script>
