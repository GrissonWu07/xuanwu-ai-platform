<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'

import PortalShell from '@/components/PortalShell.vue'
import PrimaryTabs from '@/components/PrimaryTabs.vue'
import ProfileMenu from '@/components/ProfileMenu.vue'
import StatusPill from '@/components/StatusPill.vue'
import { topStatusPills } from '@/data/portal'
import { getAuthMe, getDashboardOverview } from '@/api/management'

const statusPills = ref(topStatusPills)
const profile = ref({
  displayName: 'Gang Wu',
  subtitle: 'Platform owner',
})

function reportShellFallback(message: string, error: unknown) {
  if ((import.meta as any).env?.MODE !== 'test') {
    console.warn(message, error)
  }
}

onMounted(async () => {
  try {
    const me = await getAuthMe()
    const roleIds = Array.isArray(me.role_ids) ? me.role_ids : []
    profile.value = {
      displayName: me.display_name || me.user_id,
      subtitle: roleIds[0] || 'Platform operator',
    }
  } catch (error) {
    reportShellFallback('portal auth/me unavailable, using shell fallback', error)
  }

  try {
    const overview = await getDashboardOverview()
    statusPills.value = overview.quickStats.slice(0, 3).map((item) => ({
      label: item.label,
      value: item.value,
    }))
  } catch (error) {
    reportShellFallback('portal dashboard unavailable, using shell fallback', error)
  }
})
</script>

<template>
  <PortalShell>
    <div class="app-shell">
      <header class="topbar">
        <div class="brand-lockup">
          <div class="brand-mark">XW</div>
          <div>
            <strong>XuanWu Portal</strong>
            <span>Unified operations surface</span>
          </div>
        </div>

        <label class="search" aria-label="Global search">
          <span aria-hidden="true">Search</span>
          <input type="search" placeholder="Search devices, agents, jobs, alerts" />
        </label>

        <div class="status-cluster" aria-label="Platform status">
          <StatusPill v-for="pill in statusPills" :key="pill.label" :label="pill.label" :value="pill.value" />
        </div>

        <div class="top-actions">
          <button type="button" class="icon-button" aria-label="Notifications">4</button>
          <ProfileMenu :display-name="profile.displayName" :subtitle="profile.subtitle" />
        </div>
      </header>

      <div class="tabs-row">
        <PrimaryTabs />
      </div>

      <main class="workspace">
        <RouterView />
      </main>
    </div>
  </PortalShell>
</template>

<style scoped>
.app-shell {
  display: grid;
  gap: 1rem;
  padding: 1rem 0 1.5rem;
}

.topbar {
  display: grid;
  grid-template-columns: auto minmax(280px, 1fr) auto auto;
  gap: 1rem;
  align-items: center;
}

.brand-lockup {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 18px;
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  color: white;
  font-weight: 800;
  box-shadow: 0 16px 28px rgba(91, 71, 245, 0.24);
}

.brand-lockup strong,
.brand-lockup span {
  display: block;
}

.brand-lockup strong {
  font-size: 1rem;
}

.brand-lockup span {
  color: var(--soft);
  font-size: 0.86rem;
}

.search {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.8rem 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(91, 109, 145, 0.14);
  box-shadow: var(--shadow-soft);
}

.search span {
  color: var(--soft);
}

.search input {
  width: 100%;
  border: 0;
  outline: none;
  background: transparent;
  color: var(--text);
}

.status-cluster {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.45rem;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.icon-button {
  display: inline-grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(91, 109, 145, 0.16);
  box-shadow: var(--shadow-soft);
  font-weight: 700;
}

.tabs-row {
  display: flex;
  justify-content: center;
}

.workspace {
  min-height: calc(100vh - 11rem);
  padding-bottom: 0.5rem;
}

@media (max-width: 1200px) {
  .topbar {
    grid-template-columns: 1fr;
  }

  .status-cluster,
  .top-actions {
    justify-content: flex-start;
  }
}
</style>
