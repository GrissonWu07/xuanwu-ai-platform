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

const loading = ref(true)
const agents = ref<AgentListItem[]>([])
const providers = ref<ModelProviderItem[]>([])
const models = ref<ModelConfigItem[]>([])
const error = ref('')
const selectedAgentId = ref('')
const selectedProviderId = ref('')
const selectedModelId = ref('')
const route = useRoute()
const router = useRouter()

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

const selectedAgent = computed(
  () => agents.value.find((agent) => agent.agent_id === selectedAgentId.value) ?? agents.value[0] ?? null,
)

const selectedProvider = computed(
  () => providers.value.find((provider) => provider.provider_id === selectedProviderId.value) ?? providers.value[0] ?? null,
)

const selectedModel = computed(
  () => models.value.find((model) => model.model_id === selectedModelId.value) ?? models.value[0] ?? null,
)

const selectedModelCapabilities = computed(() => selectedModel.value?.capabilities ?? [])

const isUnavailable = computed(() => error.value.includes('503') || error.value.includes('502') || error.value.includes('500'))

async function syncQuery(next: { agentId?: string; providerId?: string; modelId?: string }) {
  await router.replace({
    query: {
      ...route.query,
      agentId: next.agentId || undefined,
      providerId: next.providerId || undefined,
      modelId: next.modelId || undefined,
    },
  })
}

async function selectAgent(agentId: string) {
  if (!agentId) {
    return
  }
  selectedAgentId.value = agentId
  if (route.query.agentId !== agentId) {
    await syncQuery({
      agentId,
      providerId: selectedProviderId.value,
      modelId: selectedModelId.value,
    })
  }
}

async function selectProvider(providerId: string) {
  if (!providerId) {
    return
  }
  selectedProviderId.value = providerId
  if (route.query.providerId !== providerId) {
    await syncQuery({
      agentId: selectedAgentId.value,
      providerId,
      modelId: selectedModelId.value,
    })
  }
}

async function selectModel(modelId: string) {
  if (!modelId) {
    return
  }
  selectedModelId.value = modelId
  if (route.query.modelId !== modelId) {
    await syncQuery({
      agentId: selectedAgentId.value,
      providerId: selectedProviderId.value,
      modelId,
    })
  }
}

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

    const requestedAgentId = typeof route.query.agentId === 'string' ? route.query.agentId : ''
    const requestedProviderId = typeof route.query.providerId === 'string' ? route.query.providerId : ''
    const requestedModelId = typeof route.query.modelId === 'string' ? route.query.modelId : ''
    const nextAgentId = agentsPayload.items.find((agent) => agent.agent_id === requestedAgentId)?.agent_id ?? agentsPayload.items[0]?.agent_id ?? ''
    const nextProviderId =
      providersPayload.items.find((provider) => provider.provider_id === requestedProviderId)?.provider_id ??
      providersPayload.items[0]?.provider_id ??
      ''
    const nextModelId = modelsPayload.items.find((model) => model.model_id === requestedModelId)?.model_id ?? modelsPayload.items[0]?.model_id ?? ''

    if (nextAgentId) {
      selectedAgentId.value = nextAgentId
    }
    if (nextProviderId) {
      selectedProviderId.value = nextProviderId
    }
    if (nextModelId) {
      selectedModelId.value = nextModelId
    }

    if (
      nextAgentId &&
      nextProviderId &&
      nextModelId &&
      (route.query.agentId !== nextAgentId || route.query.providerId !== nextProviderId || route.query.modelId !== nextModelId)
    ) {
      await syncQuery({
        agentId: nextAgentId,
        providerId: nextProviderId,
        modelId: nextModelId,
      })
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load AI config proxy resources'
  } finally {
    loading.value = false
  }
}

function handleAgentSelect(row: Record<string, string>) {
  void selectAgent(row.id)
}

function handleProviderSelect(row: Record<string, string>) {
  void selectProvider(row.id)
}

function handleModelSelect(row: Record<string, string>) {
  void selectModel(row.id)
}

watch(
  () => route.query.agentId,
  (agentId) => {
    const nextAgentId = typeof agentId === 'string' ? agentId : ''
    if (!nextAgentId || nextAgentId === selectedAgentId.value || agents.value.length === 0) {
      return
    }
    if (agents.value.some((agent) => agent.agent_id === nextAgentId)) {
      selectedAgentId.value = nextAgentId
    }
  },
)

watch(
  () => route.query.providerId,
  (providerId) => {
    const nextProviderId = typeof providerId === 'string' ? providerId : ''
    if (!nextProviderId || nextProviderId === selectedProviderId.value || providers.value.length === 0) {
      return
    }
    if (providers.value.some((provider) => provider.provider_id === nextProviderId)) {
      selectedProviderId.value = nextProviderId
    }
  },
)

watch(
  () => route.query.modelId,
  (modelId) => {
    const nextModelId = typeof modelId === 'string' ? modelId : ''
    if (!nextModelId || nextModelId === selectedModelId.value || models.value.length === 0) {
      return
    }
    if (models.value.some((model) => model.model_id === nextModelId)) {
      selectedModelId.value = nextModelId
    }
  },
)

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

    <section v-else class="surface-grid">
      <div class="table-stack">
        <DataTable
          title="Agent proxy list"
          :columns="agentColumns"
          :rows="agentRows"
          row-key="id"
          row-label-key="name"
          :selected-row-key="selectedAgent?.agent_id"
          selectable
          @row-select="handleAgentSelect"
        />
        <DataTable
          title="Provider proxy list"
          :columns="providerColumns"
          :rows="providerRows"
          row-key="id"
          row-label-key="name"
          :selected-row-key="selectedProvider?.provider_id"
          selectable
          @row-select="handleProviderSelect"
        />
        <DataTable
          title="Model proxy list"
          :columns="modelColumns"
          :rows="modelRows"
          row-key="id"
          row-label-key="label"
          :selected-row-key="selectedModel?.model_id"
          selectable
          @row-select="handleModelSelect"
        />
      </div>

      <aside class="detail-stack">
        <article v-if="selectedAgent" class="detail-panel" data-testid="agent-proxy-detail-panel">
          <header class="detail-panel__head">
            <div>
              <span class="detail-panel__eyebrow">Selected agent</span>
              <h2>{{ selectedAgent.name }}</h2>
            </div>
            <span class="detail-chip">{{ selectedAgent.status }}</span>
          </header>
          <div class="detail-grid">
            <div class="detail-card">
              <span>Provider</span>
              <strong>{{ selectedAgent.provider_id ?? 'Unassigned' }}</strong>
            </div>
            <div class="detail-card">
              <span>Model</span>
              <strong>{{ selectedAgent.model_id ?? 'Unassigned' }}</strong>
            </div>
          </div>
        </article>

        <article v-if="selectedProvider" class="detail-panel" data-testid="provider-proxy-detail-panel">
          <header class="detail-panel__head">
            <div>
              <span class="detail-panel__eyebrow">Selected provider</span>
              <h2>{{ selectedProvider.name }}</h2>
            </div>
            <span class="detail-chip">{{ selectedProvider.status }}</span>
          </header>
          <div class="detail-grid">
            <div class="detail-card">
              <span>Provider type</span>
              <strong>{{ selectedProvider.provider_type }}</strong>
            </div>
            <div class="detail-card">
              <span>Base URL</span>
              <strong>{{ selectedProvider.base_url ?? 'Managed upstream' }}</strong>
            </div>
          </div>
        </article>

        <article v-if="selectedModel" class="detail-panel" data-testid="model-proxy-detail-panel">
          <header class="detail-panel__head">
            <div>
              <span class="detail-panel__eyebrow">Selected model</span>
              <h2>{{ selectedModel.label }}</h2>
            </div>
            <span class="detail-chip">{{ selectedModel.status }}</span>
          </header>
          <div class="detail-grid">
            <div class="detail-card">
              <span>Model name</span>
              <strong>{{ selectedModel.model_name }}</strong>
            </div>
            <div class="detail-card">
              <span>Provider</span>
              <strong>{{ selectedModel.provider_id }}</strong>
            </div>
          </div>
          <div v-if="selectedModelCapabilities.length > 0" class="capability-list">
            <span v-for="capability in selectedModelCapabilities" :key="capability" class="capability-chip">
              {{ capability }}
            </span>
          </div>
        </article>
      </aside>
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

.capability-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
}

.capability-chip {
  display: inline-flex;
  padding: 0.45rem 0.75rem;
  border-radius: 999px;
  background: rgba(124, 108, 255, 0.1);
  color: var(--accent-strong);
  font-size: 0.9rem;
  font-weight: 700;
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
