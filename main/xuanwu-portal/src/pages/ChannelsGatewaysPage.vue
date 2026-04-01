<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import {
  getChannel,
  getDevices,
  getGateway,
  getGatewayOverview,
  listDiscoveredDevices,
  listChannels,
  listGateways,
  updateChannel,
  updateGateway,
  type ChannelItem,
  type DevicesCollectionResponse,
  type DiscoveredDevicesResponse,
  type GatewayItem,
  type GatewayOverviewResponse,
} from '@/api/management'

const loading = ref(true)
const channels = ref<ChannelItem[]>([])
const gateways = ref<GatewayItem[]>([])
const devices = ref<DevicesCollectionResponse['items']>([])
const discoveredDevices = ref<DiscoveredDevicesResponse['items']>([])
const gatewayOverview = ref<GatewayOverviewResponse | null>(null)
const selectedChannelId = ref('')
const selectedGatewayId = ref('')
const selectedChannel = ref<ChannelItem | null>(null)
const selectedGateway = ref<GatewayItem | null>(null)
const error = ref('')
const actionError = ref('')
const channelActionBusy = ref(false)
const gatewayActionBusy = ref(false)
const route = useRoute()
const router = useRouter()

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

const protocolSummary = computed(() =>
  Object.entries(gatewayOverview.value?.protocol_distribution ?? {})
    .sort(([, left], [, right]) => right - left)
    .map(([protocol, count]) => `${protocol} · ${count} gateway${count === 1 ? '' : 's'}`),
)

const siteSummary = computed(() =>
  Object.entries(gatewayOverview.value?.site_distribution ?? {})
    .sort(([, left], [, right]) => right - left)
    .map(([siteId, count]) => `${siteId} · ${count} route${count === 1 ? '' : 's'}`),
)

const selectedGatewayManagedDevices = computed(() =>
  devices.value.filter((item) => item.gateway_id === selectedGatewayId.value),
)

const selectedGatewayDiscoveredDevices = computed(() =>
  discoveredDevices.value.filter((item) => item.gateway_id === selectedGatewayId.value && item.discovery_status !== 'ignored'),
)

async function selectChannel(channelId: string) {
  selectedChannelId.value = channelId
  selectedChannel.value = await getChannel(channelId)

  if (route.query.channelId !== channelId) {
    await router.replace({
      query: {
        ...route.query,
        channelId,
      },
    })
  }
}

async function selectGateway(gatewayId: string) {
  selectedGatewayId.value = gatewayId
  selectedGateway.value = await getGateway(gatewayId)

  if (route.query.gatewayId !== gatewayId) {
    await router.replace({
      query: {
        ...route.query,
        gatewayId,
      },
    })
  }
}

async function loadChannelsGateways() {
  loading.value = true
  error.value = ''
  actionError.value = ''
  try {
    const [channelsPayload, gatewaysPayload, overviewPayload, devicesPayload, discoveredPayload] = await Promise.all([
      listChannels(),
      listGateways(),
      getGatewayOverview(),
      getDevices(),
      listDiscoveredDevices().catch(() => ({ items: [] })),
    ])
    channels.value = channelsPayload.items
    gateways.value = gatewaysPayload.items
    gatewayOverview.value = overviewPayload
    devices.value = devicesPayload.items
    discoveredDevices.value = discoveredPayload.items

    const requestedChannelId = typeof route.query.channelId === 'string' ? route.query.channelId : ''
    const requestedGatewayId = typeof route.query.gatewayId === 'string' ? route.query.gatewayId : ''
    const nextChannelId =
      channelsPayload.items.find((item) => item.channel_id === requestedChannelId)?.channel_id ??
      channelsPayload.items[0]?.channel_id ??
      ''
    const nextGatewayId =
      gatewaysPayload.items.find((item) => item.gateway_id === requestedGatewayId)?.gateway_id ??
      gatewaysPayload.items[0]?.gateway_id ??
      ''

    await Promise.all([
      nextChannelId ? selectChannel(nextChannelId) : Promise.resolve(),
      nextGatewayId ? selectGateway(nextGatewayId) : Promise.resolve(),
    ])
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load channels and gateways'
  } finally {
    loading.value = false
  }
}

async function pauseSelectedChannel() {
  if (!selectedChannel.value || channelActionBusy.value || selectedChannel.value.status === 'paused') {
    return
  }
  channelActionBusy.value = true
  actionError.value = ''
  try {
    const updated = await updateChannel(selectedChannel.value.channel_id, {
      ...selectedChannel.value,
      status: 'paused',
    })
    channels.value = channels.value.map((item) => (item.channel_id === updated.channel_id ? updated : item))
    selectedChannel.value = updated
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : 'Unable to pause channel.'
  } finally {
    channelActionBusy.value = false
  }
}

async function activateSelectedChannel() {
  if (!selectedChannel.value || channelActionBusy.value || selectedChannel.value.status === 'active') {
    return
  }
  channelActionBusy.value = true
  actionError.value = ''
  try {
    const updated = await updateChannel(selectedChannel.value.channel_id, {
      ...selectedChannel.value,
      status: 'active',
    })
    channels.value = channels.value.map((item) => (item.channel_id === updated.channel_id ? updated : item))
    selectedChannel.value = updated
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : 'Unable to activate channel.'
  } finally {
    channelActionBusy.value = false
  }
}

async function setGatewayMaintenance() {
  if (!selectedGateway.value || gatewayActionBusy.value || selectedGateway.value.status === 'maintenance') {
    return
  }
  gatewayActionBusy.value = true
  actionError.value = ''
  try {
    const updated = await updateGateway(selectedGateway.value.gateway_id, {
      ...selectedGateway.value,
      status: 'maintenance',
    })
    gateways.value = gateways.value.map((item) => (item.gateway_id === updated.gateway_id ? updated : item))
    selectedGateway.value = updated
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : 'Unable to update gateway.'
  } finally {
    gatewayActionBusy.value = false
  }
}

async function markGatewayHealthy() {
  if (!selectedGateway.value || gatewayActionBusy.value || selectedGateway.value.status === 'healthy') {
    return
  }
  gatewayActionBusy.value = true
  actionError.value = ''
  try {
    const updated = await updateGateway(selectedGateway.value.gateway_id, {
      ...selectedGateway.value,
      status: 'healthy',
    })
    gateways.value = gateways.value.map((item) => (item.gateway_id === updated.gateway_id ? updated : item))
    selectedGateway.value = updated
  } catch (err) {
    actionError.value = err instanceof Error ? err.message : 'Unable to update gateway.'
  } finally {
    gatewayActionBusy.value = false
  }
}

watch(
  () => route.query.channelId,
  (channelId) => {
    const nextChannelId = typeof channelId === 'string' ? channelId : ''
    if (!nextChannelId || nextChannelId === selectedChannelId.value) {
      return
    }

    const exists = channels.value.some((item) => item.channel_id === nextChannelId)
    if (exists) {
      void selectChannel(nextChannelId)
    }
  },
)

watch(
  () => route.query.gatewayId,
  (gatewayId) => {
    const nextGatewayId = typeof gatewayId === 'string' ? gatewayId : ''
    if (!nextGatewayId || nextGatewayId === selectedGatewayId.value) {
      return
    }

    const exists = gateways.value.some((item) => item.gateway_id === nextGatewayId)
    if (exists) {
      void selectGateway(nextGatewayId)
    }
  },
)

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
        <SummaryCard
          title="Gateways"
          :value="String(gatewayOverview?.total_count ?? gateways.length)"
          detail="Northbound routing endpoints"
        />
        <SummaryCard
          title="Managed devices"
          :value="String(channels.reduce((sum, item) => sum + (item.device_count ?? 0), 0))"
          detail="Reported through channels"
        />
      </section>

      <div v-if="loading" class="loading-copy">Loading channels and gateways...</div>

      <section v-else class="table-grid">
        <div class="column-stack">
          <DataTable
            title="Channel catalogue"
            :columns="channelColumns"
            :rows="channelRows"
            row-key="id"
            row-label-key="display_name"
            :selected-row-key="selectedChannelId"
            selectable
            @row-select="(row) => selectChannel(row.id)"
          />
          <aside v-if="selectedChannel" class="detail-panel" data-testid="channel-detail-panel">
            <header class="detail-head">
              <div>
                <span class="detail-eyebrow">{{ selectedChannel.channel_id }}</span>
                <h2>{{ selectedChannel.display_name || selectedChannel.channel_id }}</h2>
              </div>
              <span class="detail-chip">{{ selectedChannel.status || 'unknown' }}</span>
            </header>
            <div class="detail-grid">
              <div class="detail-card">
                <span>Owner</span>
                <strong>{{ selectedChannel.owner_user_id || 'anonymous' }}</strong>
              </div>
              <div class="detail-card">
                <span>Devices</span>
                <strong>{{ selectedChannel.device_count ?? 0 }}</strong>
              </div>
            </div>
            <div class="action-row">
              <button
                v-if="selectedChannel.status !== 'paused'"
                type="button"
                class="action-button action-button--ghost"
                :disabled="channelActionBusy"
                @click="pauseSelectedChannel"
              >
                Pause channel
              </button>
              <button
                v-if="selectedChannel.status === 'paused'"
                type="button"
                class="action-button action-button--primary"
                :disabled="channelActionBusy"
                @click="activateSelectedChannel"
              >
                Activate channel
              </button>
            </div>
          </aside>
        </div>

        <div class="column-stack">
          <DataTable
            title="Gateway inventory"
            :columns="gatewayColumns"
            :rows="gatewayRows"
            row-key="id"
            row-label-key="display_name"
            :selected-row-key="selectedGatewayId"
            selectable
            @row-select="(row) => selectGateway(row.id)"
          />
          <aside v-if="selectedGateway" class="detail-panel" data-testid="gateway-detail-panel">
            <header class="detail-head">
              <div>
                <span class="detail-eyebrow">{{ selectedGateway.gateway_id }}</span>
                <h2>{{ selectedGateway.display_name || selectedGateway.gateway_id }}</h2>
              </div>
              <span class="detail-chip">{{ selectedGateway.status || 'unknown' }}</span>
            </header>
            <div class="detail-grid">
              <div class="detail-card">
                <span>Adapter</span>
                <strong>{{ selectedGateway.adapter_type || 'unspecified' }}</strong>
              </div>
              <div class="detail-card">
                <span>Protocol</span>
                <strong>{{ selectedGateway.protocol_type || 'unknown' }}</strong>
              </div>
              <div class="detail-card">
                <span>Site</span>
                <strong>{{ selectedGateway.site_id || 'No site' }}</strong>
              </div>
              <div class="detail-card">
                <span>Managed devices</span>
                <strong>{{ selectedGatewayManagedDevices.length }}</strong>
              </div>
              <div class="detail-card">
                <span>pending discoveries</span>
                <strong>{{ selectedGatewayDiscoveredDevices.length }} pending</strong>
              </div>
            </div>
            <div class="action-row">
              <button
                v-if="selectedGateway.status !== 'maintenance'"
                type="button"
                class="action-button action-button--ghost"
                :disabled="gatewayActionBusy"
                @click="setGatewayMaintenance"
              >
                Set maintenance mode
              </button>
              <button
                v-if="selectedGateway.status === 'maintenance'"
                type="button"
                class="action-button action-button--primary"
                :disabled="gatewayActionBusy"
                @click="markGatewayHealthy"
              >
                Mark healthy
              </button>
            </div>
            <section class="detail-section">
              <h3>Managed devices</h3>
              <div class="insight-chips">
                <span
                  v-for="item in selectedGatewayManagedDevices"
                  :key="item.device_id"
                  class="insight-chip"
                >
                  {{ item.display_name || item.device_id }}
                </span>
                <span v-if="selectedGatewayManagedDevices.length === 0" class="insight-chip insight-chip--muted">
                  No managed devices
                </span>
              </div>
            </section>
            <section class="detail-section">
              <h3>Discovery queue</h3>
              <div class="insight-chips">
                <span
                  v-for="item in selectedGatewayDiscoveredDevices"
                  :key="item.discovery_id"
                  class="insight-chip insight-chip--warning"
                >
                  {{ item.display_name || item.device_id }}
                </span>
                <span v-if="selectedGatewayDiscoveredDevices.length === 0" class="insight-chip insight-chip--muted">
                  No pending discoveries
                </span>
              </div>
            </section>
          </aside>
          <article v-if="protocolSummary.length || siteSummary.length" class="insight-panel">
            <div v-if="protocolSummary.length" class="insight-section">
              <h2>Protocol distribution</h2>
              <div class="insight-chips">
                <span v-for="item in protocolSummary" :key="item" class="insight-chip">{{ item }}</span>
              </div>
            </div>
            <div v-if="siteSummary.length" class="insight-section">
              <h2>Site distribution</h2>
              <div class="insight-chips">
                <span v-for="item in siteSummary" :key="item" class="insight-chip">{{ item }}</span>
              </div>
            </div>
          </article>
        </div>
      </section>
      <p v-if="actionError" class="action-error">{{ actionError }}</p>
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

.column-stack {
  display: grid;
  gap: 1rem;
}

.detail-panel,
.insight-panel {
  display: grid;
  gap: 1rem;
  padding: 1.15rem;
  border-radius: 24px;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}

.detail-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: start;
}

.detail-head h2,
.insight-section h2 {
  margin: 0;
  font-size: 1rem;
}

.detail-eyebrow {
  display: inline-block;
  margin-bottom: 0.35rem;
  color: var(--soft);
  font-size: 0.82rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.detail-chip {
  display: inline-flex;
  padding: 0.55rem 0.8rem;
  border-radius: 999px;
  background: rgba(124, 108, 255, 0.1);
  color: var(--accent-strong);
  font-weight: 700;
  text-transform: lowercase;
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

.detail-section {
  display: grid;
  gap: 0.65rem;
}

.detail-section h3 {
  margin: 0;
  font-size: 1rem;
}

.action-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.action-button {
  min-height: 2.8rem;
  padding: 0 1rem;
  border-radius: 999px;
  border: 0;
  font-weight: 700;
  cursor: pointer;
}

.action-button--primary {
  background: var(--accent);
  color: #fff;
}

.action-button--ghost {
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(91, 109, 145, 0.16);
}

.insight-section {
  display: grid;
  gap: 0.75rem;
}

.insight-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.insight-chip {
  display: inline-flex;
  align-items: center;
  min-height: 2.25rem;
  padding: 0 0.9rem;
  border-radius: 999px;
  background: rgba(124, 108, 255, 0.1);
  color: var(--accent-strong);
  font-weight: 600;
}

.insight-chip--warning {
  background: rgba(185, 132, 20, 0.12);
  color: var(--warning);
}

.insight-chip--muted {
  background: rgba(91, 109, 145, 0.12);
  color: var(--muted);
}

.action-error {
  margin: 0;
  color: var(--danger);
  font-weight: 600;
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
