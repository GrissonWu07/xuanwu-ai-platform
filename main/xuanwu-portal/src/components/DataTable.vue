<script setup lang="ts">
export interface DataTableColumn {
  key: string
  label: string
}

defineProps<{
  title: string
  columns: DataTableColumn[]
  rows: Array<Record<string, string>>
  rowKey: string
  rowLabelKey?: string
  selectedRowKey?: string
  selectable?: boolean
}>()

const emit = defineEmits<{
  (event: 'row-select', row: Record<string, string>): void
}>()
</script>

<template>
  <section class="panel">
    <header class="panel-head">
      <h2>{{ title }}</h2>
      <span>{{ rows.length }} rows</span>
    </header>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th v-for="column in columns" :key="column.key">{{ column.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in rows"
            :key="row[rowKey]"
            :data-selected="row[rowKey] === selectedRowKey"
          >
            <td v-for="(column, index) in columns" :key="column.key">
              <button
                v-if="selectable && index === 0"
                class="row-trigger"
                type="button"
                :aria-label="row[rowLabelKey ?? column.key]"
                @click="emit('row-select', row)"
              >
                {{ row[column.key] }}
              </button>
              <template v-else>
                {{ row[column.key] }}
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<style scoped>
.panel {
  padding: 1.2rem;
  border-radius: 24px;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
}

.panel-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
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

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 540px;
}

th,
td {
  text-align: left;
  padding: 0.9rem 0.75rem;
  border-bottom: 1px solid rgba(91, 109, 145, 0.12);
}

th {
  color: var(--muted);
  font-weight: 600;
  font-size: 0.88rem;
}

td {
  color: var(--text);
}

tbody tr[data-selected='true'] {
  background: rgba(124, 108, 255, 0.08);
}

.row-trigger {
  padding: 0;
  font-weight: 700;
  color: inherit;
}
</style>
