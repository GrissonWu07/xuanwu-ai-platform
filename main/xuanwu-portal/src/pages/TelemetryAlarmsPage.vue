<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import {
  getAlarm,
  getAlertsOverview,
  listAlarms,
  listEvents,
  listTelemetry,
  type AlarmDetailResponse,
  type AlertsOverviewResponse,
  type EventItem,
  type TelemetryItem,
} from '@/api/management'

type AlarmItem = AlertsOverviewResponse['alerts'][number]

const loading = ref(true)
const error = ref('')
const overview = ref<AlertsOverviewResponse | null>(null)
const telemetry = ref<TelemetryItem[]>([])
const events = ref<EventItem[]>([])
const alarms = ref<AlarmItem[]>([])
const selectedTelemetryId = ref('')
const selectedEventId = ref('')
const selectedAlarmId = ref('')
const selectedAlarmDetail = ref<AlarmDetailResponse | null>(null)
const route = useRoute()
const router = useRouter()

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

const selectedTelemetry = computed(
  () => telemetry.value.find((item) => item.telemetry_id === selectedTelemetryId.value) ?? telemetry.value[0] ?? null,
)

const selectedEvent = computed(
  () => events.value.find((item) => item.event_id === selectedEventId.value) ?? events.value[0] ?? null,
)

const selectedAlarm = computed(
  () => alarms.value.find((item) => item.alarm_id === selectedAlarmId.value) ?? alarms.value[0] ?? null,
)

async function syncQuery(next: { telemetryId?: string; eventId?: string; alarmId?: string }) {
  await router.replace({
    query: {
      ...route.query,
      telemetryId: next.telemetryId || undefined,
      eventId: next.eventId || undefined,
      alarmId: next.alarmId || undefined,
    },
  })
}

async function loadAlarmDetail(alarmId: string) {
  selectedAlarmId.value = alarmId
  try {
    selectedAlarmDetail.value = await getAlarm(alarmId)
  } catch {
    selectedAlarmDetail.value = null
  }
}

async function selectTelemetry(telemetryId: string) {
  if (!telemetryId) {
    return
  }
  selectedTelemetryId.value = telemetryId
  if (route.query.telemetryId !== telemetryId) {
    await syncQuery({
      telemetryId,
      eventId: selectedEventId.value,
      alarmId: selectedAlarmId.value,
    })
  }
}

async function selectEvent(eventId: string) {
  if (!eventId) {
    return
  }
  selectedEventId.value = eventId
  if (route.query.eventId !== eventId) {
    await syncQuery({
      telemetryId: selectedTelemetryId.value,
      eventId,
      alarmId: selectedAlarmId.value,
    })
  }
}

async function selectAlarm(alarmId: string) {
  if (!alarmId) {
    return
  }
  await loadAlarmDetail(alarmId)
  if (route.query.alarmId !== alarmId) {
    await syncQuery({
      telemetryId: selectedTelemetryId.value,
      eventId: selectedEventId.value,
      alarmId,
    })
  }
}

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

    const requestedTelemetryId = typeof route.query.telemetryId === 'string' ? route.query.telemetryId : ''
    const requestedEventId = typeof route.query.eventId === 'string' ? route.query.eventId : ''
    const requestedAlarmId = typeof route.query.alarmId === 'string' ? route.query.alarmId : ''

    const nextTelemetryId =
      telemetryPayload.items.find((item) => item.telemetry_id === requestedTelemetryId)?.telemetry_id ??
      telemetryPayload.items[0]?.telemetry_id ??
      ''
    const nextEventId =
      eventsPayload.items.find((item) => item.event_id === requestedEventId)?.event_id ?? eventsPayload.items[0]?.event_id ?? ''
    const nextAlarmId =
      alarmsPayload.items.find((item) => item.alarm_id === requestedAlarmId)?.alarm_id ?? alarmsPayload.items[0]?.alarm_id ?? ''

    if (nextTelemetryId) {
      selectedTelemetryId.value = nextTelemetryId
    }
    if (nextEventId) {
      selectedEventId.value = nextEventId
    }
    if (nextAlarmId) {
      await loadAlarmDetail(nextAlarmId)
    }

    if (
      nextTelemetryId &&
      nextEventId &&
      nextAlarmId &&
      (route.query.telemetryId !== nextTelemetryId || route.query.eventId !== nextEventId || route.query.alarmId !== nextAlarmId)
    ) {
      await syncQuery({
        telemetryId: nextTelemetryId,
        eventId: nextEventId,
        alarmId: nextAlarmId,
      })
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load telemetry and alarms'
  } finally {
    loading.value = false
  }
}

function handleTelemetrySelect(row: Record<string, string>) {
  void selectTelemetry(row.id)
}

function handleEventSelect(row: Record<string, string>) {
  void selectEvent(row.id)
}

function handleAlarmSelect(row: Record<string, string>) {
  void selectAlarm(row.id)
}

watch(
  () => route.query.telemetryId,
  (telemetryId) => {
    const nextTelemetryId = typeof telemetryId === 'string' ? telemetryId : ''
    if (!nextTelemetryId || nextTelemetryId === selectedTelemetryId.value || telemetry.value.length === 0) {
      return
    }
    if (telemetry.value.some((item) => item.telemetry_id === nextTelemetryId)) {
      selectedTelemetryId.value = nextTelemetryId
    }
  },
)

watch(
  () => route.query.eventId,
  (eventId) => {
    const nextEventId = typeof eventId === 'string' ? eventId : ''
    if (!nextEventId || nextEventId === selectedEventId.value || events.value.length === 0) {
      return
    }
    if (events.value.some((item) => item.event_id === nextEventId)) {
      selectedEventId.value = nextEventId
    }
  },
)

watch(
  () => route.query.alarmId,
  (alarmId) => {
    const nextAlarmId = typeof alarmId === 'string' ? alarmId : ''
    if (!nextAlarmId || nextAlarmId === selectedAlarmId.value || alarms.value.length === 0) {
      return
    }
    if (alarms.value.some((item) => item.alarm_id === nextAlarmId)) {
      void loadAlarmDetail(nextAlarmId)
    }
  },
)

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

      <section v-else class="surface-grid">
        <div class="table-stack">
          <DataTable
            title="Telemetry stream"
            :columns="telemetryColumns"
            :rows="telemetryRows"
            row-key="id"
            row-label-key="capability_code"
            :selected-row-key="selectedTelemetry?.telemetry_id"
            selectable
            @row-select="handleTelemetrySelect"
          />
          <DataTable
            title="Event stream"
            :columns="eventColumns"
            :rows="eventRows"
            row-key="id"
            row-label-key="event_type"
            :selected-row-key="selectedEvent?.event_id"
            selectable
            @row-select="handleEventSelect"
          />
          <DataTable
            title="Alarm roster"
            :columns="alarmColumns"
            :rows="alarmRows"
            row-key="id"
            row-label-key="title"
            :selected-row-key="selectedAlarm?.alarm_id"
            selectable
            @row-select="handleAlarmSelect"
          />
        </div>

        <aside class="detail-stack">
          <article v-if="selectedTelemetry" class="detail-panel" data-testid="telemetry-detail-panel">
            <header class="detail-panel__head">
              <div>
                <span class="detail-panel__eyebrow">Selected telemetry</span>
                <h2>{{ selectedTelemetry.capability_code }}</h2>
              </div>
            </header>
            <div class="detail-grid">
              <div class="detail-card">
                <span>Device</span>
                <strong>{{ selectedTelemetry.device_id ?? 'Unknown' }}</strong>
              </div>
              <div class="detail-card">
                <span>Value</span>
                <strong>{{ String(selectedTelemetry.value ?? 'Unknown') }}</strong>
              </div>
              <div class="detail-card detail-card--wide">
                <span>Reported at</span>
                <strong>{{ selectedTelemetry.reported_at ?? 'Unknown' }}</strong>
              </div>
            </div>
          </article>

          <article v-if="selectedEvent" class="detail-panel" data-testid="event-detail-panel">
            <header class="detail-panel__head">
              <div>
                <span class="detail-panel__eyebrow">Selected event</span>
                <h2>{{ selectedEvent.event_type }}</h2>
              </div>
              <span class="detail-chip">{{ selectedEvent.severity ?? 'info' }}</span>
            </header>
            <div class="detail-grid">
              <div class="detail-card">
                <span>Device</span>
                <strong>{{ selectedEvent.device_id ?? 'Unknown' }}</strong>
              </div>
              <div class="detail-card">
                <span>Gateway</span>
                <strong>{{ selectedEvent.gateway_id ?? 'Unknown' }}</strong>
              </div>
              <div class="detail-card detail-card--wide">
                <span>Occurred at</span>
                <strong>{{ selectedEvent.occurred_at ?? 'Unknown' }}</strong>
              </div>
            </div>
          </article>

          <article v-if="selectedAlarmDetail || selectedAlarm" class="detail-panel" data-testid="alarm-detail-panel">
            <header class="detail-panel__head">
              <div>
                <span class="detail-panel__eyebrow">Selected alarm</span>
                <h2>{{ selectedAlarmDetail?.title ?? selectedAlarm?.title }}</h2>
              </div>
              <span class="detail-chip">{{ selectedAlarmDetail?.severity ?? selectedAlarm?.severity }}</span>
            </header>
            <div class="detail-grid">
              <div class="detail-card">
                <span>Source</span>
                <strong>{{ selectedAlarmDetail?.source ?? selectedAlarm?.source ?? 'Unknown' }}</strong>
              </div>
              <div class="detail-card">
                <span>Status</span>
                <strong>{{ selectedAlarmDetail?.status ?? selectedAlarm?.status ?? 'Unknown' }}</strong>
              </div>
              <div v-if="selectedAlarmDetail?.gateway_id" class="detail-card">
                <span>Gateway</span>
                <strong>{{ selectedAlarmDetail.gateway_id }}</strong>
              </div>
              <div v-if="selectedAlarmDetail?.device_id" class="detail-card">
                <span>Device</span>
                <strong>{{ selectedAlarmDetail.device_id }}</strong>
              </div>
            </div>
            <p v-if="selectedAlarmDetail?.message" class="detail-copy">
              {{ selectedAlarmDetail.message }}
            </p>
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

.table-stack {
  display: grid;
  gap: 1rem;
}

.detail-stack {
  display: grid;
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

.detail-card--wide {
  grid-column: 1 / -1;
}

.detail-card span {
  color: var(--muted);
}

.detail-copy {
  margin: 0;
  color: var(--muted);
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
