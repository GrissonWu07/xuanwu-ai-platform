<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { profileMenuItems } from '@/data/portal'

const props = withDefaults(
  defineProps<{
    displayName?: string
    subtitle?: string
  }>(),
  {
    displayName: 'Gang Wu',
    subtitle: 'Platform owner',
  },
)

const open = ref(false)

const avatarLabel = computed(() =>
  props.displayName
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('') || 'XW',
)

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
      :aria-label="`${displayName} profile menu`"
      :aria-expanded="open ? 'true' : 'false'"
      aria-haspopup="menu"
    >
      <span class="avatar">{{ avatarLabel }}</span>
      <span class="profile-label">
        <strong>{{ displayName }}</strong>
        <small>{{ subtitle }}</small>
      </span>
      <span aria-hidden="true">v</span>
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
