<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { getAuthMe, getPortalConfig, type AuthMeResponse, type PortalConfigResponse } from '@/api/management'

const loading = ref(true)
const config = ref<PortalConfigResponse | null>(null)
const me = ref<AuthMeResponse | null>(null)
const error = ref('')
const selectedFeatureId = ref('')
const selectedEndpointId = ref('')
const route = useRoute()
const router = useRouter()

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
    enabled: enabled ? 'Enabled' : 'Disabled',
  })),
)

const selectedFeature = computed(
  () =>
    featureRows.value.find((item) => item.id === selectedFeatureId.value) ??
    featureRows.value[0] ??
    null,
)

const selectedEndpoint = computed(
  () =>
    endpointRows.value.find((item) => item.id === selectedEndpointId.value) ??
    endpointRows.value[0] ??
    null,
)

async function syncQuery(next: { featureId?: string; endpointId?: string }) {
  await router.replace({
    query: {
      ...route.query,
      featureId: next.featureId || undefined,
      endpointId: next.endpointId || undefined,
    },
  })
}

async function selectFeature(featureId: string) {
  if (!featureId) {
    return
  }

  selectedFeatureId.value = featureId
  if (route.query.featureId !== featureId) {
    await syncQuery({
      featureId,
      endpointId: selectedEndpointId.value,
    })
  }
}

async function selectEndpoint(endpointId: string) {
  if (!endpointId) {
    return
  }

  selectedEndpointId.value = endpointId
  if (route.query.endpointId !== endpointId) {
    await syncQuery({
      featureId: selectedFeatureId.value,
      endpointId,
    })
  }
}

async function loadSettings() {
  loading.value = true
  error.value = ''

  try {
    const [mePayload, configPayload] = await Promise.all([getAuthMe(), getPortalConfig()])
    me.value = mePayload
    config.value = configPayload

    const requestedFeatureId = typeof route.query.featureId === 'string' ? route.query.featureId : ''
    const requestedEndpointId = typeof route.query.endpointId === 'string' ? route.query.endpointId : ''
    const nextFeatureId =
      featureRows.value.find((item) => item.id === requestedFeatureId)?.id ?? featureRows.value[0]?.id ?? ''
    const nextEndpointId =
      endpointRows.value.find((item) => item.id === requestedEndpointId)?.id ?? endpointRows.value[0]?.id ?? ''

    if (nextFeatureId) {
      selectedFeatureId.value = nextFeatureId
    }
    if (nextEndpointId) {
      selectedEndpointId.value = nextEndpointId
    }

    if (
      nextFeatureId &&
      nextEndpointId &&
      (route.query.featureId !== nextFeatureId || route.query.endpointId !== nextEndpointId)
    ) {
      await syncQuery({
        featureId: nextFeatureId,
        endpointId: nextEndpointId,
      })
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load portal settings'
  } finally {
    loading.value = false
  }
}

function handleFeatureSelect(row: Record<string, string>) {
  void selectFeature(row.id)
}

function handleEndpointSelect(row: Record<string, string>) {
  void selectEndpoint(row.id)
}

watch(
  () => route.query.featureId,
  (featureId) => {
    const nextFeatureId = typeof featureId === 'string' ? featureId : ''
    if (!nextFeatureId || nextFeatureId === selectedFeatureId.value || featureRows.value.length === 0) {
      return
    }

    if (featureRows.value.some((item) => item.id === nextFeatureId)) {
      selectedFeatureId.value = nextFeatureId
    }
  },
)

watch(
  () => route.query.endpointId,
  (endpointId) => {
    const nextEndpointId = typeof endpointId === 'string' ? endpointId : ''
    if (!nextEndpointId || nextEndpointId === selectedEndpointId.value || endpointRows.value.length === 0) {
      return
    }

    if (endpointRows.value.some((item) => item.id === nextEndpointId)) {
      selectedEndpointId.value = nextEndpointId
    }
  },
)

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

      <section v-else class="surface-grid">
        <div class="table-stack">
          <DataTable
            title="Feature flags"
            :columns="featureColumns"
            :rows="featureRows"
            row-key="id"
            row-label-key="name"
            :selected-row-key="selectedFeature?.id"
            selectable
            @row-select="handleFeatureSelect"
          />
          <DataTable
            title="Service endpoints"
            :columns="endpointColumns"
            :rows="endpointRows"
            row-key="id"
            row-label-key="name"
            :selected-row-key="selectedEndpoint?.id"
            selectable
            @row-select="handleEndpointSelect"
          />
        </div>

        <aside class="detail-stack">
          <article v-if="selectedFeature" class="panel" data-testid="feature-detail-panel">
            <header class="panel-head">
              <div>
                <span class="detail-eyebrow">Selected feature</span>
                <h2>{{ selectedFeature.name }}</h2>
              </div>
              <span>Feature flag</span>
            </header>
            <div class="detail-grid">
              <div class="detail-card">
                <span>Status</span>
                <strong>{{ selectedFeature.enabled }}</strong>
              </div>
              <div class="detail-card">
                <span>Audience</span>
                <strong>Portal operators</strong>
              </div>
            </div>
          </article>

          <article v-if="selectedEndpoint" class="panel" data-testid="endpoint-detail-panel">
            <header class="panel-head">
              <div>
                <span class="detail-eyebrow">Selected endpoint</span>
                <h2>{{ selectedEndpoint.name }}</h2>
              </div>
              <span>Reachable URL</span>
            </header>
            <div class="detail-grid">
              <div class="detail-card detail-card--wide">
                <span>Service URL</span>
                <strong>{{ selectedEndpoint.url }}</strong>
              </div>
              <div class="detail-card">
                <span>Purpose</span>
                <strong>{{ selectedEndpoint.name }} API</strong>
              </div>
            </div>
          </article>
        </aside>
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

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.surface-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(320px, 0.9fr);
  gap: 1rem;
}

.table-stack,
.detail-stack {
  display: grid;
  gap: 1rem;
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

.panel-head h2 {
  margin: 0.3rem 0 0;
}

.detail-eyebrow {
  color: var(--soft);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.detail-card {
  display: grid;
  gap: 0.35rem;
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(124, 108, 255, 0.06);
}

.detail-card span {
  color: var(--muted);
}

.detail-card--wide {
  grid-column: 1 / -1;
}

@media (max-width: 960px) {
  .page-head,
  .metric-grid,
  .surface-grid,
  .detail-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
