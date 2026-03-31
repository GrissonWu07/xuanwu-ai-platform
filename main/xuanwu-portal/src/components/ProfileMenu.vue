<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

import { profileMenuItems } from '@/data/portal'

const open = ref(false)

function toggleMenu() {
  open.value = !open.value
}

function closeMenu() {
  open.value = false
}
</script>

<template>
  <div class="profile-menu">
    <button
      class="profile-trigger"
      type="button"
      @click="toggleMenu"
      aria-label="Gang Wu profile menu"
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="menu"
    >
      <span class="avatar">GW</span>
      <span class="profile-label">
        <strong>Gang Wu</strong>
        <small>Platform owner</small>
      </span>
      <span aria-hidden="true">▾</span>
    </button>

    <div v-if="open" class="menu" role="menu">
      <RouterLink
        v-for="item in profileMenuItems"
        :key="item.label"
        :to="item.to"
        role="menuitem"
        class="menu-item"
        @click="closeMenu"
      >
        {{ item.label }}
      </RouterLink>
    </div>
  </div>
</template>

<style scoped>
.profile-menu {
  position: relative;
}

.profile-trigger {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.45rem 0.65rem 0.45rem 0.45rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(91, 109, 145, 0.16);
  box-shadow: var(--shadow-soft);
}

.avatar {
  display: inline-grid;
  place-items: center;
  width: 2.3rem;
  height: 2.3rem;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  color: white;
  font-weight: 700;
}

.profile-label {
  display: grid;
  text-align: left;
}

.profile-label strong {
  font-size: 0.92rem;
}

.profile-label small {
  color: var(--soft);
  font-size: 0.75rem;
}

.menu {
  position: absolute;
  right: 0;
  top: calc(100% + 0.65rem);
  min-width: 220px;
  padding: 0.5rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.97);
  border: 1px solid rgba(91, 109, 145, 0.18);
  box-shadow: var(--shadow);
  z-index: 10;
}

.menu-item {
  display: block;
  padding: 0.7rem 0.8rem;
  border-radius: 12px;
  color: var(--text);
}

.menu-item:hover,
.menu-item:focus-visible {
  background: rgba(124, 108, 255, 0.09);
}
</style>
