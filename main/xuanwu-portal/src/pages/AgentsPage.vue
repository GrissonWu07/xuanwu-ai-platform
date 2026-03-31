<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

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

const agents = ref<AgentListItem[]>([])
const providers = ref<ModelProviderItem[]>([])
const models = ref<ModelConfigItem[]>([])
const selectedAgentId = ref('')
const loadError = ref('')
const upstreamUnavailable = ref(false)
const route = useRoute()
const router = useRouter()

const columns: DataTableColumn[] = [
  { key: 'name', label: 'Agent' },
  { key: 'status', label: 'Status' },
  { key: 'provider', label: 'Provider' },
  { key: 'model', label: 'Model' },
]

const summaryCards = computed(() => [
  { title: 'Agents', value: String(agents.value.length), detail: 'Visible through the proxy surface', tone: 'accent' as const },
  { title: 'Providers', value: String(providers.value.length), detail: 'Available model providers', tone: 'blue' as const },
  { title: 'Models', value: String(models.value.length), detail: 'Proxy-exposed model configs', tone: 'green' as const },
])

const providerMap = computed(() => new Map(providers.value.map((item) => [item.provider_id, item])))
const modelMap = computed(() => new Map(models.value.map((item) => [item.model_id, item])))

const tableRows = computed(() =>
  agents.value.map((item) => ({
    id: item.agent_id,
    name: item.name,
    status: item.status,
    provider: providerMap.value.get(item.provider_id || '')?.name || item.provider_id || 'Unassigned',
    model: modelMap.value.get(item.model_id || '')?.label || item.model_id || 'Unassigned',
  })),
)

const selectedAgent = computed(
  () => agents.value.find((item) => item.agent_id === selectedAgentId.value) ?? agents.value[0] ?? null,
)

const selectedProvider = computed(() =>
  selectedAgent.value?.provider_id ? providerMap.value.get(selectedAgent.value.provider_id) : null,
)

const selectedModel = computed(() =>
  selectedAgent.value?.model_id ? modelMap.value.get(selectedAgent.value.model_id) : null,
)

async function selectAgent(agentId: string) {
  selectedAgentId.value = agentId

  if (route.query.agentId !== agentId) {
    await router.replace({
      query: {
        ...route.query,
        agentId,
      },
    })
  }
}

async function loadProxyData() {
  loadError.value = ''
  upstreamUnavailable.value = false

  const [agentsResult, providersResult, modelsResult] = await Promise.allSettled([
    listAgents(),
    listModelProviders(),
    listModels(),
  ])

  if (agentsResult.status === 'fulfilled') {
    agents.value = agentsResult.value.items
  } else {
    upstreamUnavailable.value = true
    loadError.value = agentsResult.reason instanceof Error ? agentsResult.reason.message : 'Agent proxy unavailable.'
  }

  if (providersResult.status === 'fulfilled') {
    providers.value = providersResult.value.items
  } else {
    upstreamUnavailable.value = true
  }

  if (modelsResult.status === 'fulfilled') {
    models.value = modelsResult.value.items
  } else {
    upstreamUnavailable.value = true
  }

  const requestedAgentId = typeof route.query.agentId === 'string' ? route.query.agentId : ''
  const nextAgentId =
    agents.value.find((item) => item.agent_id === requestedAgentId)?.agent_id ?? agents.value[0]?.agent_id ?? ''
  if (nextAgentId) {
    await selectAgent(nextAgentId)
    return
  }

  selectedAgentId.value = ''
}

function handleRowSelect(row: Record<string, string>) {
  void selectAgent(row.id)
}

watch(
  () => route.query.agentId,
  (agentId) => {
    const nextAgentId = typeof agentId === 'string' ? agentId : ''
    if (!nextAgentId || nextAgentId === selectedAgentId.value) {
      return
    }

    const exists = agents.value.some((item) => item.agent_id === nextAgentId)
    if (exists) {
      selectedAgentId.value = nextAgentId
    }
  },
)

onMounted(() => {
  void loadProxyData()
})
</script>

<template>
  <section class="agents-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">XuanWu proxy domain</span>
        <h1>Agents</h1>
        <p>Review upstream agent resources through the local proxy and stay aware of upstream availability.</p>
      </div>
    </header>

    <section class="metric-grid" aria-label="Agents metrics">
      <SummaryCard
        v-for="item in summaryCards"
        :key="item.title"
        :title="item.title"
        :value="item.value"
        :detail="item.detail"
        :tone="item.tone"
      />
    </section>

    <div class="surface-grid">
      <div class="left-stack">
        <UpstreamUnavailableState
          v-if="upstreamUnavailable"
          title="XuanWu upstream unavailable"
          detail="Agent proxy data is temporarily unavailable while the XuanWu upstream reconnects."
        />

        <DataTable
          title="Agent catalogue"
          :columns="columns"
          :rows="tableRows"
          row-key="id"
          row-label-key="name"
          :selected-row-key="selectedAgent?.agent_id"
          selectable
          @row-select="handleRowSelect"
        />
      </div>

      <aside v-if="selectedAgent" class="detail-panel" data-testid="agent-detail-panel">
        <header class="detail-panel__head">
          <div>
            <span class="detail-panel__eyebrow">{{ selectedAgent.agent_id }}</span>
            <h2>{{ selectedAgent.name }}</h2>
          </div>
          <span class="detail-chip">{{ selectedAgent.status }}</span>
        </header>

        <div class="detail-grid">
          <div class="detail-card">
            <span>Provider</span>
            <strong>{{ selectedProvider?.name || selectedAgent.provider_id || 'Unassigned' }}</strong>
          </div>
          <div class="detail-card">
            <span>Model</span>
            <strong>{{ selectedModel?.label || selectedAgent.model_id || 'Unassigned' }}</strong>
          </div>
          <div class="detail-card">
            <span>Updated at</span>
            <strong>{{ selectedAgent.updated_at || 'Unknown' }}</strong>
          </div>
          <div class="detail-card">
            <span>Capabilities</span>
            <strong>{{ selectedModel?.capabilities?.join(', ') || 'Not reported' }}</strong>
          </div>
        </div>
      </aside>

      <EmptyState
        v-else
        title="Agent proxy unavailable"
        :detail="loadError || 'Agent proxy data is temporarily unavailable while XuanWu reconnects.'"
      />
    </div>
  </section>
</template>

<style scoped>
.agents-page {
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
  max-width: 44rem;
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

.left-stack {
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

.detail-card span {
  color: var(--muted);
}

@media (max-width: 1120px) {
  .metric-grid,
  .surface-grid {
    grid-template-columns: 1fr;
  }
}
</style>
