<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ActivityFeed from '@/components/ActivityFeed.vue'
import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { ackAlarm, getAlertsOverview, listAlarms, type AlertsOverviewResponse } from '@/api/management'

type AlarmItem = AlertsOverviewResponse['alerts'][number]

const overview = ref<AlertsOverviewResponse | null>(null)
const alarms = ref<AlarmItem[]>([])
const selectedAlarmId = ref('')
const loadError = ref('')
const isAcking = ref(false)

const columns: DataTableColumn[] = [
  { key: 'title', label: 'Alert' },
  { key: 'severity', label: 'Severity' },
  { key: 'status', label: 'Status' },
  { key: 'source', label: 'Source' },
]

const summaryCards = computed(() => overview.value?.summary ?? [])

const tableRows = computed(() =>
  alarms.value.map((item) => ({
    id: item.alarm_id,
    title: item.title,
    severity: item.severity,
    status: item.status,
    source: item.source,
  })),
)

const selectedAlarm = computed(
  () => alarms.value.find((item) => item.alarm_id === selectedAlarmId.value) ?? alarms.value[0] ?? null,
)

const activityItems = computed(
  () =>
    overview.value?.activity.map((item) => ({
      title: item.title,
      meta: `${item.at} · ${item.detail}`,
    })) ?? [],
)

async function loadAlerts() {
  loadError.value = ''

  try {
    const [overviewResponse, alarmsResponse] = await Promise.all([getAlertsOverview(), listAlarms()])
    overview.value = overviewResponse
    alarms.value = alarmsResponse.items
    selectedAlarmId.value = alarmsResponse.items[0]?.alarm_id ?? ''
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Alerts overview is unavailable.'
  }
}

function handleRowSelect(row: Record<string, string>) {
  selectedAlarmId.value = row.id
}

async function acknowledgeSelectedAlarm() {
  if (!selectedAlarm.value || selectedAlarm.value.status === 'acknowledged' || isAcking.value) {
    return
  }

  isAcking.value = true

  try {
    await ackAlarm(selectedAlarm.value.alarm_id)
    alarms.value = alarms.value.map((item) =>
      item.alarm_id === selectedAlarm.value?.alarm_id ? { ...item, status: 'acknowledged' } : item,
    )
  } finally {
    isAcking.value = false
  }
}

onMounted(() => {
  void loadAlerts()
})
</script>

<template>
  <section class="alerts-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Alarms and operational response</span>
        <h1>Alerts</h1>
        <p>Review active alarms, acknowledge issues, and keep incident context visible without a noisy wall.</p>
      </div>
    </header>

    <div v-if="loadError" class="surface-grid">
      <EmptyState title="Alerts unavailable" :detail="loadError" />
    </div>

    <template v-else>
      <section class="metric-grid" aria-label="Alerts metrics">
        <SummaryCard
          v-for="item in summaryCards"
          :key="item.label"
          :title="item.label"
          :value="item.value"
          detail="Live platform read model"
          tone="amber"
        />
      </section>

      <div class="surface-grid">
        <DataTable
          title="Alert list"
          :columns="columns"
          :rows="tableRows"
          row-key="id"
          row-label-key="title"
          :selected-row-key="selectedAlarm?.alarm_id"
          selectable
          @row-select="handleRowSelect"
        />

        <aside v-if="selectedAlarm" class="detail-panel" data-testid="alert-detail-panel">
          <header class="detail-panel__head">
            <div>
              <span class="detail-panel__eyebrow">{{ selectedAlarm.source }}</span>
              <h2>{{ selectedAlarm.title }}</h2>
            </div>
            <span class="detail-chip" :data-severity="selectedAlarm.severity">{{ selectedAlarm.severity }}</span>
          </header>

          <div class="detail-grid">
            <div class="detail-card">
              <span>Status</span>
              <strong>{{ selectedAlarm.status }}</strong>
            </div>
            <div class="detail-card">
              <span>Created at</span>
              <strong>{{ selectedAlarm.created_at || 'Unknown' }}</strong>
            </div>
          </div>

          <div class="detail-actions">
            <button
              type="button"
              class="ack-button"
              :disabled="selectedAlarm.status === 'acknowledged' || isAcking"
              @click="acknowledgeSelectedAlarm"
            >
              {{ selectedAlarm.status === 'acknowledged' ? 'Acknowledged' : 'Acknowledge alert' }}
            </button>
          </div>

          <section class="detail-section">
            <h3>Operational activity</h3>
            <ActivityFeed v-if="activityItems.length > 0" :items="activityItems" />
            <EmptyState v-else title="No alert activity" detail="Alert activity will appear here as operators respond." />
          </section>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.alerts-page {
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

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
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
  background: rgba(209, 77, 87, 0.1);
  color: var(--danger);
  font-weight: 700;
  text-transform: lowercase;
}

.detail-chip[data-severity='medium'] {
  background: rgba(185, 132, 20, 0.12);
  color: var(--warning);
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
  background: rgba(209, 77, 87, 0.06);
}

.detail-card span {
  color: var(--muted);
}

.detail-actions {
  display: flex;
  justify-content: flex-start;
}

.ack-button {
  min-height: 2.8rem;
  padding: 0 1rem;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  color: white;
  font-weight: 700;
}

.ack-button:disabled {
  cursor: default;
  opacity: 0.6;
}

.detail-section {
  display: grid;
  gap: 0.8rem;
}

.detail-section h3 {
  margin: 0;
  font-size: 1rem;
}

@media (max-width: 1120px) {
  .metric-grid,
  .surface-grid {
    grid-template-columns: 1fr;
  }
}
</style>
