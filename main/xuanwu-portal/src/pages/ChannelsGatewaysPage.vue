<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { listChannels, listGateways, type ChannelItem, type GatewayItem } from '@/api/management'

const loading = ref(true)
const channels = ref<ChannelItem[]>([])
const gateways = ref<GatewayItem[]>([])
const error = ref('')

const channelColumns: DataTableColumn[] = [
  { key: 'display_name', label: 'Channel' },
  { key: 'owner_user_id', label: 'Owner' },
  { key: 'status', label: 'Status' },
  { key: 'device_count', label: 'Devices' },
]

const gatewayColumns: DataTableColumn[] = [
  { key: 'display_name', label: 'Gateway' },
  { key: 'adapter_type', label: 'Adapter' },
  { key: 'status', label: 'Status' },
  { key: 'site_id', label: 'Site' },
]

const channelRows = computed(() =>
  channels.value.map((channel) => ({
    id: channel.channel_id,
    display_name: channel.display_name ?? channel.channel_id,
    owner_user_id: channel.owner_user_id ?? 'anonymous',
    status: channel.status ?? 'unknown',
    device_count: String(channel.device_count ?? 0),
  })),
)

const gatewayRows = computed(() =>
  gateways.value.map((gateway) => ({
    id: gateway.gateway_id,
    display_name: gateway.display_name ?? gateway.gateway_id,
    adapter_type: gateway.adapter_type ?? 'unspecified',
    status: gateway.status ?? 'unknown',
    site_id: gateway.site_id ?? 'No site',
  })),
)

async function loadChannelsGateways() {
  loading.value = true
  error.value = ''
  try {
    const [channelsPayload, gatewaysPayload] = await Promise.all([listChannels(), listGateways()])
    channels.value = channelsPayload.items
    gateways.value = gatewaysPayload.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load channels and gateways'
  } finally {
    loading.value = false
  }
}

onMounted(loadChannelsGateways)
</script>

<template>
  <section class="secondary-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Profile destination</span>
        <h1>Channels &amp; Gateways</h1>
        <p>Inspect the user-facing control spaces and the gateway fleet that routes device traffic across protocols.</p>
      </div>
      <button type="button" class="ghost-action" @click="loadChannelsGateways">Refresh</button>
    </header>

    <div v-if="error">
      <EmptyState title="Channels & Gateways unavailable" :detail="error" />
    </div>

    <template v-else>
      <section class="metric-grid" aria-label="Channels and gateways metrics">
        <SummaryCard title="Channels" :value="String(channels.length)" detail="User-owned control surfaces" />
        <SummaryCard title="Gateways" :value="String(gateways.length)" detail="Northbound routing endpoints" />
        <SummaryCard title="Managed devices" :value="String(channels.reduce((sum, item) => sum + (item.device_count ?? 0), 0))" detail="Reported through channels" />
      </section>

      <div v-if="loading" class="loading-copy">Loading channels and gateways...</div>

      <section v-else class="table-grid">
        <DataTable title="Channel catalogue" :columns="channelColumns" :rows="channelRows" row-key="id" />
        <DataTable title="Gateway inventory" :columns="gatewayColumns" :rows="gatewayRows" row-key="id" />
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

@media (max-width: 960px) {
  .page-head,
  .metric-grid,
  .table-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
