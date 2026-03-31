<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import UpstreamUnavailableState from '@/components/UpstreamUnavailableState.vue'
import {
  listAgents,
  listModelProviders,
  listModels,
  type AgentListItem,
  type ModelConfigItem,
  type ModelProviderItem,
} from '@/api/management'

const loading = ref(true)
const agents = ref<AgentListItem[]>([])
const providers = ref<ModelProviderItem[]>([])
const models = ref<ModelConfigItem[]>([])
const error = ref('')

const agentColumns: DataTableColumn[] = [
  { key: 'name', label: 'Agent' },
  { key: 'status', label: 'Status' },
  { key: 'provider_id', label: 'Provider' },
  { key: 'model_id', label: 'Model' },
]

const providerColumns: DataTableColumn[] = [
  { key: 'name', label: 'Provider' },
  { key: 'provider_type', label: 'Type' },
  { key: 'status', label: 'Status' },
  { key: 'base_url', label: 'Base URL' },
]

const modelColumns: DataTableColumn[] = [
  { key: 'label', label: 'Model config' },
  { key: 'model_name', label: 'Model' },
  { key: 'provider_id', label: 'Provider' },
  { key: 'status', label: 'Status' },
]

const agentRows = computed(() =>
  agents.value.map((agent) => ({
    id: agent.agent_id,
    name: agent.name,
    status: agent.status,
    provider_id: agent.provider_id ?? 'Unassigned',
    model_id: agent.model_id ?? 'Unassigned',
  })),
)

const providerRows = computed(() =>
  providers.value.map((provider) => ({
    id: provider.provider_id,
    name: provider.name,
    provider_type: provider.provider_type,
    status: provider.status,
    base_url: provider.base_url ?? 'Managed upstream',
  })),
)

const modelRows = computed(() =>
  models.value.map((model) => ({
    id: model.model_id,
    label: model.label,
    model_name: model.model_name,
    provider_id: model.provider_id,
    status: model.status,
  })),
)

const isUnavailable = computed(() => error.value.includes('503') || error.value.includes('502') || error.value.includes('500'))

async function loadProxyResources() {
  loading.value = true
  error.value = ''
  try {
    const [agentsPayload, providersPayload, modelsPayload] = await Promise.all([
      listAgents(),
      listModelProviders(),
      listModels(),
    ])
    agents.value = agentsPayload.items
    providers.value = providersPayload.items
    models.value = modelsPayload.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load AI config proxy resources'
  } finally {
    loading.value = false
  }
}

onMounted(loadProxyResources)
</script>

<template>
  <section class="secondary-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Profile destination</span>
        <h1>AI Config Proxy</h1>
        <p>Inspect proxied agents, model providers, and model configs without duplicating `XuanWu` truth in this repository.</p>
      </div>
      <button type="button" class="ghost-action" @click="loadProxyResources">Refresh</button>
    </header>

    <section class="metric-grid" aria-label="AI config proxy metrics">
      <SummaryCard title="Agents" :value="String(agents.length)" detail="Proxied through management" />
      <SummaryCard title="Providers" :value="String(providers.length)" detail="Upstream provider catalogue" />
      <SummaryCard title="Models" :value="String(models.length)" detail="Model config inventory" />
    </section>

    <div v-if="error && !isUnavailable">
      <EmptyState title="AI Config Proxy unavailable" :detail="error" />
    </div>

    <UpstreamUnavailableState
      v-else-if="error && isUnavailable"
      title="XuanWu upstream is unavailable"
      :detail="error"
    />

    <div v-else-if="loading" class="loading-copy">Loading proxied AI configuration...</div>

    <section v-else class="table-stack">
      <DataTable title="Agent proxy list" :columns="agentColumns" :rows="agentRows" row-key="id" />
      <DataTable title="Provider proxy list" :columns="providerColumns" :rows="providerRows" row-key="id" />
      <DataTable title="Model proxy list" :columns="modelColumns" :rows="modelRows" row-key="id" />
    </section>
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
