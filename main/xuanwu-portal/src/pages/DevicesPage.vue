<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ActivityFeed from '@/components/ActivityFeed.vue'
import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import { getDeviceDetail, getDevices, type DeviceDetailResponse, type DevicesCollectionResponse } from '@/api/management'

const devices = ref<DevicesCollectionResponse['items']>([])
const selectedDeviceId = ref('')
const detail = ref<DeviceDetailResponse | null>(null)
const search = ref('')
const loadError = ref('')
const route = useRoute()
const router = useRouter()

const columns: DataTableColumn[] = [
  { key: 'name', label: 'Device' },
  { key: 'status', label: 'Lifecycle' },
  { key: 'bind', label: 'Binding' },
  { key: 'owner', label: 'Owner' },
  { key: 'runtime', label: 'Last seen' },
]

const tableRows = computed(() =>
  devices.value
    .filter((item) => {
      const keyword = search.value.trim().toLowerCase()
      if (!keyword) {
        return true
      }

      return [item.device_id, item.display_name, item.owner_user_id, item.device_type, item.protocol_type]
        .filter(Boolean)
        .some((value) => String(value).toLowerCase().includes(keyword))
    })
    .map((item) => ({
      id: item.device_id,
      name: item.display_name || item.device_id,
      status: item.lifecycle_status,
      bind: item.bind_status,
      owner: item.owner_user_id,
      runtime: item.last_seen_at || 'No signal',
    })),
)

async function loadDeviceDetail(deviceId: string) {
  selectedDeviceId.value = deviceId
  detail.value = await getDeviceDetail(deviceId)
}

async function selectDevice(deviceId: string) {
  if (!deviceId) {
    return
  }

  await loadDeviceDetail(deviceId)

  if (route.query.deviceId !== deviceId) {
    await router.replace({
      query: {
        ...route.query,
        deviceId,
      },
    })
  }
}

async function loadDevices() {
  loadError.value = ''

  try {
    const response = await getDevices()
    devices.value = response.items

    const requestedDeviceId = typeof route.query.deviceId === 'string' ? route.query.deviceId : ''
    const nextDeviceId =
      response.items.find((item) => item.device_id === requestedDeviceId)?.device_id ?? response.items[0]?.device_id ?? ''

    if (nextDeviceId) {
      await selectDevice(nextDeviceId)
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Device inventory is unavailable.'
  }
}

function handleRowSelect(row: Record<string, string>) {
  void selectDevice(row.id)
}

watch(
  () => route.query.deviceId,
  (deviceId) => {
    const nextDeviceId = typeof deviceId === 'string' ? deviceId : ''
    if (!nextDeviceId || nextDeviceId === selectedDeviceId.value || devices.value.length === 0) {
      return
    }

    const exists = devices.value.some((item) => item.device_id === nextDeviceId)
    if (exists) {
      void loadDeviceDetail(nextDeviceId)
    }
  },
)

const detailActivity = computed(
  () =>
    detail.value?.recent_events.map((item) => ({
      title: item.title,
      meta: `${item.at} · ${item.detail}`,
    })) ?? [],
)

onMounted(() => {
  void loadDevices()
})
</script>

<template>
  <section class="devices-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Ownership and runtime</span>
        <h1>Devices</h1>
        <p>Review lifecycle, binding, and runtime context for the fleet from one working surface.</p>
      </div>
      <label class="page-filter">
        <span class="sr-only">Filter devices</span>
        <input v-model="search" type="search" placeholder="Filter by name, owner, protocol" />
      </label>
    </header>

    <div v-if="loadError" class="surface-grid">
      <EmptyState title="Devices unavailable" :detail="loadError" />
    </div>

    <div v-else class="surface-grid">
      <DataTable
        title="Registered devices"
        :columns="columns"
        :rows="tableRows"
        row-key="id"
        row-label-key="name"
        :selected-row-key="selectedDeviceId"
        selectable
        @row-select="handleRowSelect"
      />

      <aside v-if="detail" class="detail-panel" data-testid="device-detail-panel">
        <header class="detail-panel__head">
          <div>
            <span class="detail-panel__eyebrow">{{ detail.device.device_type }} · {{ detail.device.protocol_type }}</span>
            <h2>{{ detail.device.display_name || detail.device.device_id }}</h2>
          </div>
          <span class="detail-chip">{{ detail.runtime?.session_status || 'unknown' }}</span>
        </header>

        <div class="detail-grid">
          <div class="detail-card">
            <span>Agent</span>
            <strong>{{ detail.binding?.agent_id || 'Unassigned' }}</strong>
          </div>
          <div class="detail-card">
            <span>Channel</span>
            <strong>{{ detail.binding?.channel_id || 'Unassigned' }}</strong>
          </div>
          <div class="detail-card">
            <span>Model</span>
            <strong>{{ detail.binding?.model_config_id || 'Not linked' }}</strong>
          </div>
          <div class="detail-card">
            <span>Capability routes</span>
            <strong>{{ detail.runtime?.capability_route_count ?? 0 }}</strong>
          </div>
        </div>

        <section class="detail-section">
          <h3>Recent telemetry</h3>
          <div v-for="metric in detail.recent_telemetry" :key="`${metric.metric}-${metric.at}`" class="metric-line">
            <span>{{ metric.metric }}</span>
            <strong>{{ metric.value }}</strong>
          </div>
        </section>

        <section class="detail-section">
          <h3>Recent activity</h3>
          <ActivityFeed :items="detailActivity" />
        </section>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.devices-page {
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
  margin: 0.25rem 0 0.4rem;
  font-size: clamp(2rem, 3vw, 2.8rem);
  letter-spacing: -0.05em;
}

.page-head p {
  margin: 0;
  max-width: 42rem;
  color: var(--muted);
}

.page-filter input {
  min-width: 280px;
  border: 1px solid rgba(91, 109, 145, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.84);
  padding: 0.9rem 1rem;
  box-shadow: var(--shadow-soft);
}

.surface-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 1fr);
  gap: 1rem;
}

.detail-panel {
  display: grid;
  gap: 1rem;
  padding: 1.2rem;
  border-radius: 24px;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}

.detail-panel__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.detail-panel__eyebrow {
  display: inline-block;
  margin-bottom: 0.4rem;
  color: var(--soft);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.detail-panel__head h2 {
  margin: 0;
  font-size: 1.4rem;
}

.detail-chip {
  display: inline-flex;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  background: rgba(124, 108, 255, 0.1);
  color: var(--accent-strong);
  font-weight: 700;
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

.detail-card span,
.metric-line span {
  color: var(--muted);
}

.detail-section {
  display: grid;
  gap: 0.8rem;
}

.detail-section h3 {
  margin: 0;
  font-size: 1rem;
}

.metric-line {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.8rem 0.9rem;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(91, 109, 145, 0.12);
}

@media (max-width: 1120px) {
  .page-head,
  .surface-grid {
    display: grid;
    grid-template-columns: 1fr;
  }

  .page-filter input {
    min-width: 0;
    width: 100%;
  }
}

@media (max-width: 720px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
