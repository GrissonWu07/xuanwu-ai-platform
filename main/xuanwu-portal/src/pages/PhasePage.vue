<script setup lang="ts">
import { computed } from 'vue'

import ActivityFeed from '@/components/ActivityFeed.vue'
import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import FilterToolbar from '@/components/FilterToolbar.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import UpstreamUnavailableState from '@/components/UpstreamUnavailableState.vue'

const props = defineProps<{
  title: string
  eyebrow: string
  description: string
  metrics: Array<{ label: string; value: string }>
  filters?: string[]
  highlights?: Array<{ title: string; fields: string[] }>
  tableTitle: string
  tableColumns: string[]
  tableRows: string[][]
  activityTitle: string
  activity: Array<{ title: string; meta: string }>
  upstream?: { title: string; detail: string }
}>()

const tableColumns = computed<DataTableColumn[]>(() =>
  props.tableColumns.map((label, index) => ({
    key: `column_${index}`,
    label,
  })),
)

const tableRows = computed(() =>
  props.tableRows.map((row, rowIndex) => {
    const record: Record<string, string> = { id: `${props.title}-${rowIndex}` }

    row.forEach((value, columnIndex) => {
      record[`column_${columnIndex}`] = value
    })

    return record
  }),
)
</script>

<template>
  <section class="phase-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">{{ eyebrow }}</span>
        <h1>{{ title }}</h1>
        <p>{{ description }}</p>
      </div>
      <div class="head-actions">
        <button type="button" class="ghost-action">Refresh</button>
        <button type="button" class="primary-action">Create view</button>
      </div>
    </header>

    <FilterToolbar v-if="filters?.length" :title="`${title} search`" :chips="filters" />

    <section class="metric-grid" :aria-label="`${title} metrics`">
      <SummaryCard
        v-for="metric in metrics"
        :key="metric.label"
        :title="metric.label"
        :value="metric.value"
        detail="Phase 1 skeleton"
      />
    </section>

    <section v-if="highlights?.length" class="highlight-grid" :aria-label="`${title} field structure`">
      <article v-for="item in highlights" :key="item.title" class="highlight-card">
        <h2>{{ item.title }}</h2>
        <ul>
          <li v-for="field in item.fields" :key="field">{{ field }}</li>
        </ul>
      </article>
    </section>

    <section class="main-grid">
      <DataTable :title="tableTitle" :columns="tableColumns" :rows="tableRows" row-key="id" />
      <div class="side-stack">
        <article class="panel">
          <header class="panel-head">
            <h2>{{ activityTitle }}</h2>
            <span>Recent</span>
          </header>
          <ActivityFeed :items="activity" />
        </article>
        <UpstreamUnavailableState v-if="upstream" :title="upstream.title" :detail="upstream.detail" />
      </div>
    </section>
  </section>
</template>

<style scoped>
.phase-page {
  display: grid;
  gap: 1rem;
}

.page-head {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: end;
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
  max-width: 48rem;
  color: var(--muted);
}

.head-actions {
  display: flex;
  gap: 0.65rem;
}

.ghost-action,
.primary-action {
  min-height: 2.85rem;
  padding: 0 1rem;
  border-radius: 999px;
  font-weight: 700;
}

.ghost-action {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(91, 109, 145, 0.16);
}

.primary-action {
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  color: white;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.highlight-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.highlight-card {
  padding: 1.2rem;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(91, 109, 145, 0.14);
  box-shadow: var(--shadow-soft);
}

.highlight-card h2 {
  margin: 0 0 0.75rem;
  font-size: 1rem;
}

.highlight-card ul {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--muted);
  display: grid;
  gap: 0.45rem;
}

.main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(280px, 1fr);
  gap: 1rem;
}

.side-stack {
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
  margin-bottom: 1rem;
}

.panel-head h2 {
  margin: 0;
  font-size: 1.05rem;
}

.panel-head span {
  color: var(--soft);
  font-size: 0.9rem;
}

@media (max-width: 1120px) {
  .page-head,
  .main-grid {
    grid-template-columns: 1fr;
    display: grid;
  }

  .head-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 800px) {
  .metric-grid {
    grid-template-columns: 1fr;
  }

  .highlight-grid {
    grid-template-columns: 1fr;
  }
}
</style>
