<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { getAlertsOverview, listAlarms, listEvents, listTelemetry, type AlertsOverviewResponse, type EventItem, type TelemetryItem } from '@/api/management'

type AlarmItem = AlertsOverviewResponse['alerts'][number]

const loading = ref(true)
const error = ref('')
const overview = ref<AlertsOverviewResponse | null>(null)
const telemetry = ref<TelemetryItem[]>([])
const events = ref<EventItem[]>([])
const alarms = ref<AlarmItem[]>([])

const telemetryColumns: DataTableColumn[] = [
  { key: 'capability_code', label: 'Capability' },
  { key: 'device_id', label: 'Device' },
  { key: 'value', label: 'Value' },
  { key: 'reported_at', label: 'Reported at' },
]

const eventColumns: DataTableColumn[] = [
  { key: 'event_type', label: 'Event' },
  { key: 'severity', label: 'Severity' },
  { key: 'device_id', label: 'Device' },
  { key: 'occurred_at', label: 'Occurred at' },
]

const alarmColumns: DataTableColumn[] = [
  { key: 'title', label: 'Alarm' },
  { key: 'severity', label: 'Severity' },
  { key: 'status', label: 'Status' },
  { key: 'source', label: 'Source' },
]

const summaryCards = computed(() => [
  {
    title: 'Telemetry samples',
    value: String(telemetry.value.length),
    detail: 'Latest management stream',
    tone: 'blue' as const,
  },
  {
    title: 'Event stream',
    value: String(events.value.length),
    detail: 'Current event records',
    tone: 'green' as const,
  },
  {
    title: 'Open alerts',
    value: overview.value?.summary.find((item) => item.label === 'Active alerts')?.value ?? String(alarms.value.filter((item) => item.status !== 'acknowledged').length),
    detail: 'Derived from alarm state',
    tone: 'amber' as const,
  },
])

const telemetryRows = computed(() =>
  telemetry.value.map((item) => ({
    id: item.telemetry_id,
    capability_code: item.capability_code,
    device_id: item.device_id ?? 'Unknown',
    value: String(item.value ?? 'Unknown'),
    reported_at: item.reported_at ?? 'Unknown',
  })),
)

const eventRows = computed(() =>
  events.value.map((item) => ({
    id: item.event_id,
    event_type: item.event_type,
    severity: item.severity ?? 'info',
    device_id: item.device_id ?? item.gateway_id ?? 'Unknown',
    occurred_at: item.occurred_at ?? 'Unknown',
  })),
)

const alarmRows = computed(() =>
  alarms.value.map((item) => ({
    id: item.alarm_id,
    title: item.title,
    severity: item.severity,
    status: item.status,
    source: item.source,
  })),
)

async function loadTelemetryAndAlarms() {
  loading.value = true
  error.value = ''

  try {
    const [overviewPayload, telemetryPayload, eventsPayload, alarmsPayload] = await Promise.all([
      getAlertsOverview(),
      listTelemetry(),
      listEvents(),
      listAlarms(),
    ])

    overview.value = overviewPayload
    telemetry.value = telemetryPayload.items
    events.value = eventsPayload.items
    alarms.value = alarmsPayload.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load telemetry and alarms'
  } finally {
    loading.value = false
  }
}

onMounted(loadTelemetryAndAlarms)
</script>

<template>
  <section class="secondary-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Profile destination</span>
        <h1>Telemetry &amp; Alarms</h1>
        <p>Inspect the live operational exhaust from devices, watch the event stream, and review alarms in one focused workspace.</p>
      </div>
      <button type="button" class="ghost-action" @click="loadTelemetryAndAlarms">Refresh</button>
    </header>

    <div v-if="error">
      <EmptyState title="Telemetry & Alarms unavailable" :detail="error" />
    </div>

    <template v-else>
      <section class="metric-grid" aria-label="Telemetry and alarms metrics">
        <SummaryCard
          v-for="item in summaryCards"
          :key="item.title"
          :title="item.title"
          :value="item.value"
          :detail="item.detail"
          :tone="item.tone"
        />
      </section>

      <div v-if="loading" class="loading-copy">Loading telemetry and alarms...</div>

      <section v-else class="table-stack">
        <DataTable title="Telemetry stream" :columns="telemetryColumns" :rows="telemetryRows" row-key="id" />
        <DataTable title="Event stream" :columns="eventColumns" :rows="eventRows" row-key="id" />
        <DataTable title="Alarm roster" :columns="alarmColumns" :rows="alarmRows" row-key="id" />
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

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.table-stack {
  display: grid;
  gap: 1rem;
}

@media (max-width: 960px) {
  .page-head,
  .metric-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
