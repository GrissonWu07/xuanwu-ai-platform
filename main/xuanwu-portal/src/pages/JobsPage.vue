<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import ActivityFeed from '@/components/ActivityFeed.vue'
import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { getJobsOverview, type JobsOverviewResponse } from '@/api/management'

const overview = ref<JobsOverviewResponse | null>(null)
const selectedScheduleId = ref('')
const loadError = ref('')

const columns: DataTableColumn[] = [
  { key: 'name', label: 'Schedule' },
  { key: 'executor', label: 'Executor' },
  { key: 'cron', label: 'Schedule' },
  { key: 'status', label: 'State' },
]

const summaryCards = computed(() => overview.value?.summary ?? [])
const schedules = computed(() => overview.value?.schedules ?? [])
const runs = computed(() => overview.value?.runs ?? [])

const tableRows = computed(() =>
  schedules.value.map((item) => ({
    id: item.schedule_id,
    name: item.name,
    executor: item.executor_type,
    cron: item.schedule,
    status: item.status,
  })),
)

const selectedSchedule = computed(
  () => schedules.value.find((item) => item.schedule_id === selectedScheduleId.value) ?? schedules.value[0] ?? null,
)

const selectedRuns = computed(() =>
  runs.value
    .filter((item) => item.schedule_id === selectedSchedule.value?.schedule_id)
    .map((item) => ({
      title: item.job_run_id,
      meta: `${item.status} · ${item.executor_type} · ${item.started_at || 'Pending start'}`,
    })),
)

async function loadOverview() {
  loadError.value = ''

  try {
    const response = await getJobsOverview()
    overview.value = response
    selectedScheduleId.value = response.schedules[0]?.schedule_id ?? ''
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Jobs overview is unavailable.'
  }
}

function handleRowSelect(row: Record<string, string>) {
  selectedScheduleId.value = row.id
}

onMounted(() => {
  void loadOverview()
})
</script>

<template>
  <section class="jobs-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Scheduler and run history</span>
        <h1>Jobs</h1>
        <p>Inspect schedules, queue health, and recent job execution history from one calm workspace.</p>
      </div>
    </header>

    <div v-if="loadError" class="surface-grid">
      <EmptyState title="Jobs unavailable" :detail="loadError" />
    </div>

    <template v-else>
      <section class="metric-grid" aria-label="Jobs metrics">
        <SummaryCard
          v-for="item in summaryCards"
          :key="item.label"
          :title="item.label"
          :value="item.value"
          detail="Live platform read model"
          tone="accent"
        />
      </section>

      <div class="surface-grid">
        <DataTable
          title="Schedules"
          :columns="columns"
          :rows="tableRows"
          row-key="id"
          row-label-key="name"
          :selected-row-key="selectedSchedule?.schedule_id"
          selectable
          @row-select="handleRowSelect"
        />

        <aside v-if="selectedSchedule" class="detail-panel" data-testid="job-detail-panel">
          <header class="detail-panel__head">
            <div>
              <span class="detail-panel__eyebrow">{{ selectedSchedule.executor_type }} executor</span>
              <h2>{{ selectedSchedule.name }}</h2>
            </div>
            <span class="detail-chip">{{ selectedSchedule.status }}</span>
          </header>

          <div class="detail-grid">
            <div class="detail-card">
              <span>Cron</span>
              <strong>{{ selectedSchedule.schedule }}</strong>
            </div>
            <div class="detail-card">
              <span>Next run</span>
              <strong>{{ selectedSchedule.next_run_at || 'Pending' }}</strong>
            </div>
          </div>

          <section class="detail-section">
            <h3>Recent runs</h3>
            <ActivityFeed v-if="selectedRuns.length > 0" :items="selectedRuns" />
            <EmptyState
              v-else
              title="No recent runs"
              detail="This schedule has not emitted any run history in the local read model yet."
            />
          </section>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.jobs-page {
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
