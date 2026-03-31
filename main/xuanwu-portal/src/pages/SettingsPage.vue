<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { getAuthMe, getPortalConfig, type AuthMeResponse, type PortalConfigResponse } from '@/api/management'

const loading = ref(true)
const config = ref<PortalConfigResponse | null>(null)
const me = ref<AuthMeResponse | null>(null)
const error = ref('')

const endpointColumns: DataTableColumn[] = [
  { key: 'name', label: 'Endpoint' },
  { key: 'url', label: 'URL' },
]

const featureColumns: DataTableColumn[] = [
  { key: 'name', label: 'Feature' },
  { key: 'enabled', label: 'Enabled' },
]

const endpointRows = computed(() =>
  Object.entries(config.value?.endpoints ?? {}).map(([name, url]) => ({
    id: name,
    name,
    url,
  })),
)

const featureRows = computed(() =>
  Object.entries(config.value?.features ?? {}).map(([name, enabled]) => ({
    id: name,
    name,
    enabled: enabled ? 'Yes' : 'No',
  })),
)

async function loadSettings() {
  loading.value = true
  error.value = ''

  try {
    const [mePayload, configPayload] = await Promise.all([getAuthMe(), getPortalConfig()])
    me.value = mePayload
    config.value = configPayload
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load portal settings'
  } finally {
    loading.value = false
  }
}

onMounted(loadSettings)
</script>

<template>
  <section class="secondary-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Profile destination</span>
        <h1>Settings</h1>
        <p>Review portal feature flags, service endpoints, and the current signed-in operator profile.</p>
      </div>
      <button type="button" class="ghost-action" @click="loadSettings">Refresh</button>
    </header>

    <div v-if="error">
      <EmptyState title="Settings unavailable" :detail="error" />
    </div>

    <template v-else>
      <section class="metric-grid" aria-label="Settings metrics">
        <SummaryCard title="Product" :value="config?.brand?.product_name ?? 'XuanWu Portal'" :detail="config?.brand?.support_email ?? 'No support email'" />
        <SummaryCard title="Features" :value="String(Object.keys(config?.features ?? {}).length)" detail="Portal feature flags" />
        <SummaryCard title="Endpoints" :value="String(Object.keys(config?.endpoints ?? {}).length)" detail="Visible service URLs" />
      </section>

      <article v-if="me" class="panel">
        <header class="panel-head">
          <h2>Operator profile</h2>
          <span>{{ me.user_id }}</span>
        </header>
        <p class="profile-copy">{{ me.display_name }} can currently reach {{ me.permissions.length }} permissions through {{ me.role_ids.length }} roles.</p>
      </article>

      <div v-if="loading" class="loading-copy">Loading portal configuration...</div>

      <section v-else class="table-grid">
        <DataTable title="Feature flags" :columns="featureColumns" :rows="featureRows" row-key="id" />
        <DataTable title="Service endpoints" :columns="endpointColumns" :rows="endpointRows" row-key="id" />
      </section>
    </template>
  </section>
</template>

<style scoped>
.secondary-page {
  display: grid;
  gap: 1rem;
}

.page-head {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 1rem;
}

.eyebrow {
  color: var(--accent-strong);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-head h1 {
  margin: 0.2rem 0 0.35rem;
  font-size: clamp(1.9rem, 3vw, 2.6rem);
}

.page-head p,
.profile-copy,
.loading-copy {
  margin: 0;
  color: var(--muted);
}

.ghost-action {
  min-height: 2.85rem;
  padding: 0 1rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(91, 109, 145, 0.16);
  font-weight: 700;
}

.metric-grid,
.table-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.table-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.panel {
  padding: 1.2rem;
  border-radius: 24px;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

@media (max-width: 960px) {
  .page-head,
  .metric-grid,
  .table-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
