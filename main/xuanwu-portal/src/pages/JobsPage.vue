<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import ActivityFeed from '@/components/ActivityFeed.vue'
import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import {
  getJobRun,
  getJobsOverview,
  getJobSchedule,
  pauseJobSchedule,
  resumeJobSchedule,
  triggerJobSchedule,
  type JobRunDetailResponse,
  type JobsOverviewResponse,
  type JobScheduleDetailResponse,
} from '@/api/management'

const overview = ref<JobsOverviewResponse | null>(null)
const selectedScheduleId = ref('')
const selectedScheduleDetail = ref<JobScheduleDetailResponse | null>(null)
const selectedRunDetail = ref<JobRunDetailResponse | null>(null)
const loadError = ref('')
const actionBusy = ref(false)
const actionError = ref('')
const route = useRoute()
const router = useRouter()

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

const schedulePayloadEntries = computed(() =>
  Object.entries(selectedScheduleDetail.value?.payload ?? {}).filter(([, value]) => value !== undefined && value !== null),
)

const selectedRunSummary = computed(() => {
  if (selectedRunDetail.value?.error?.message) {
    return selectedRunDetail.value.error.message
  }

  const details = selectedRunDetail.value?.result?.details
  if (details) {
    const firstEntry = Object.entries(details).find(([, value]) => value !== undefined && value !== null)
    if (firstEntry) {
      return `${firstEntry[0]}: ${firstEntry[1]}`
    }
  }

  return 'No additional run details'
})

async function loadScheduleDetail(scheduleId: string) {
  try {
    selectedScheduleId.value = scheduleId
    selectedScheduleDetail.value = await getJobSchedule(scheduleId)
    const latestRun = runs.value.find((item) => item.schedule_id === scheduleId)
    if (latestRun) {
      selectedRunDetail.value = await getJobRun(latestRun.job_run_id)
      return
    }
  } catch {
    selectedScheduleDetail.value = null
    selectedRunDetail.value = null
  }
}

function patchScheduleOverview(scheduleId: string, patch: Partial<JobsOverviewResponse['schedules'][number]>) {
  if (!overview.value) {
    return
  }
  overview.value = {
    ...overview.value,
    schedules: overview.value.schedules.map((item) =>
      item.schedule_id === scheduleId
        ? {
            ...item,
            ...patch,
          }
        : item,
    ),
  }
}

function upsertJobRun(run: JobRunDetailResponse) {
  if (!overview.value) {
    return
  }
  const nextRuns = overview.value.runs.filter((item) => item.job_run_id !== run.job_run_id)
  nextRuns.unshift({
    job_run_id: run.job_run_id,
    schedule_id: run.schedule_id,
    status: run.status,
    executor_type: run.executor_type,
    started_at: run.started_at,
    finished_at: run.finished_at,
  })
  overview.value = {
    ...overview.value,
    runs: nextRuns,
  }
}

async function pauseSelectedSchedule() {
  if (!selectedScheduleId.value || actionBusy.value) {
    return
  }
  actionBusy.value = true
  actionError.value = ''
  try {
    const updated = await pauseJobSchedule(selectedScheduleId.value, 'Paused from portal Jobs view')
    selectedScheduleDetail.value = updated
    patchScheduleOverview(selectedScheduleId.value, { status: updated.status ?? 'disabled' })
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : 'Unable to pause schedule.'
  } finally {
    actionBusy.value = false
  }
}

async function resumeSelectedSchedule() {
  if (!selectedScheduleId.value || actionBusy.value) {
    return
  }
  actionBusy.value = true
  actionError.value = ''
  try {
    const updated = await resumeJobSchedule(selectedScheduleId.value, 'Resumed from portal Jobs view')
    selectedScheduleDetail.value = updated
    patchScheduleOverview(selectedScheduleId.value, { status: updated.status ?? 'active' })
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : 'Unable to resume schedule.'
  } finally {
    actionBusy.value = false
  }
}

async function triggerSelectedSchedule() {
  if (!selectedScheduleId.value || actionBusy.value) {
    return
  }
  actionBusy.value = true
  actionError.value = ''
  try {
    const run = await triggerJobSchedule(selectedScheduleId.value)
    selectedRunDetail.value = run
    upsertJobRun(run)
  } catch (error) {
    actionError.value = error instanceof Error ? error.message : 'Unable to run schedule now.'
  } finally {
    actionBusy.value = false
  }
}

async function selectSchedule(scheduleId: string) {
  await loadScheduleDetail(scheduleId)

  if (route.query.scheduleId !== scheduleId) {
    await router.replace({
      query: {
        ...route.query,
        scheduleId,
      },
    })
  }
}

async function loadOverview() {
  loadError.value = ''

  try {
    const response = await getJobsOverview()
    overview.value = response
    const requestedScheduleId = typeof route.query.scheduleId === 'string' ? route.query.scheduleId : ''
    const nextScheduleId =
      response.schedules.find((item) => item.schedule_id === requestedScheduleId)?.schedule_id ??
      response.schedules[0]?.schedule_id ??
      ''
    if (nextScheduleId) {
      await selectSchedule(nextScheduleId)
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Jobs overview is unavailable.'
  }
}

function handleRowSelect(row: Record<string, string>) {
  void selectSchedule(row.id)
}

watch(
  () => route.query.scheduleId,
  (scheduleId) => {
    const nextScheduleId = typeof scheduleId === 'string' ? scheduleId : ''
    if (!nextScheduleId || nextScheduleId === selectedScheduleId.value || schedules.value.length === 0) {
      return
    }

    const exists = schedules.value.some((item) => item.schedule_id === nextScheduleId)
    if (exists) {
      void loadScheduleDetail(nextScheduleId)
    }
  },
)

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
            <div v-if="selectedScheduleDetail?.timezone" class="detail-card">
              <span>Timezone</span>
              <strong>{{ selectedScheduleDetail.timezone }}</strong>
            </div>
            <div v-if="selectedRunDetail?.scheduled_for" class="detail-card">
              <span>Scheduled for</span>
              <strong>{{ selectedRunDetail.scheduled_for }}</strong>
            </div>
          </div>

          <section v-if="schedulePayloadEntries.length > 0" class="detail-section">
            <h3>Schedule payload</h3>
            <div class="payload-grid">
              <div v-for="[key, value] in schedulePayloadEntries" :key="key" class="detail-card">
                <span>{{ key }}</span>
                <strong>{{ value }}</strong>
              </div>
            </div>
          </section>

          <section v-if="selectedRunDetail" class="detail-section">
            <h3>Latest run detail</h3>
            <div class="detail-card detail-card--wide">
              <span>{{ selectedRunDetail.job_run_id }}</span>
              <strong>{{ selectedRunSummary }}</strong>
            </div>
          </section>

          <section class="detail-section">
            <div class="detail-section__head">
              <h3>Schedule actions</h3>
              <span class="detail-section__hint">Pause noisy schedules, resume quiet ones, or trigger a run immediately.</span>
            </div>
            <div class="action-row">
              <button
                v-if="selectedSchedule.status !== 'disabled'"
                type="button"
                class="action-button action-button--ghost"
                :disabled="actionBusy"
                @click="pauseSelectedSchedule"
              >
                Pause schedule
              </button>
              <button
                v-if="selectedSchedule.status === 'disabled'"
                type="button"
                class="action-button action-button--primary"
                :disabled="actionBusy"
                @click="resumeSelectedSchedule"
              >
                Resume schedule
              </button>
              <button
                type="button"
                class="action-button action-button--primary"
                :disabled="actionBusy"
                @click="triggerSelectedSchedule"
              >
                Run now
              </button>
            </div>
            <p v-if="actionError" class="action-error">{{ actionError }}</p>
          </section>

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

.detail-card--wide {
  background: rgba(124, 108, 255, 0.08);
}

.detail-card span {
  color: var(--muted);
}

.payload-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.85rem;
}

.detail-section {
  display: grid;
  gap: 0.8rem;
}

.detail-section__head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: baseline;
}

.detail-section__hint {
  color: var(--muted);
  font-size: 0.82rem;
}

.detail-section h3 {
  margin: 0;
  font-size: 1rem;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.action-button {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0.72rem 1.1rem;
  font: inherit;
  font-weight: 700;
  cursor: pointer;
  transition:
    transform 180ms ease,
    box-shadow 180ms ease,
    opacity 180ms ease;
}

.action-button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

.action-button:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 16px 28px rgba(65, 46, 109, 0.14);
}

.action-button--primary {
  background: linear-gradient(135deg, var(--accent-strong), #7f6bff);
  border-color: transparent;
  color: white;
}

.action-button--ghost {
  background: rgba(124, 108, 255, 0.08);
  color: var(--text);
}

.action-error {
  margin: 0;
  color: #b42318;
  font-size: 0.92rem;
}

@media (max-width: 1120px) {
  .metric-grid,
  .surface-grid,
  .payload-grid {
    grid-template-columns: 1fr;
  }
}
</style>
