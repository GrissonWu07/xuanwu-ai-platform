<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import ActivityFeed from '@/components/ActivityFeed.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { getDashboardOverview, type DashboardOverview } from '@/api/management'

const dashboard = ref<DashboardOverview | null>(null)
const isLoading = ref(true)
const loadError = ref('')

const hero = computed(() => dashboard.value?.hero)
const quickStats = computed(() => dashboard.value?.quickStats ?? [])
const todaySummary = computed(() => dashboard.value?.todaySummary ?? [])
const liveActivity = computed(
  () =>
    dashboard.value?.liveActivity.map((item) => ({
      title: item.title,
      meta: `${item.at} · ${item.detail}`,
      to: item.to,
    })) ?? [],
)

const quickCardRoutes: Record<string, string> = {
  devices: '/devices',
  agents: '/agents',
  jobs: '/jobs',
  alerts: '/alerts',
}

async function loadDashboard() {
  isLoading.value = true
  loadError.value = ''

  try {
    dashboard.value = await getDashboardOverview()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'Dashboard overview is unavailable.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <section class="overview">
    <div v-if="hero" class="hero">
      <div class="hero-copy">
        <span class="eyebrow">Unified operations portal</span>
        <h1>{{ hero.title }}</h1>
        <p>{{ hero.subtitle }}</p>
        <div class="hero-actions">
          <RouterLink class="primary-action" to="/devices">{{ hero.primaryAction }}</RouterLink>
          <RouterLink class="secondary-action" to="/jobs">{{ hero.secondaryAction }}</RouterLink>
        </div>
      </div>
      <div class="hero-summary">
        <div v-for="item in dashboard?.statusPills ?? []" :key="item.label" class="summary-line">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
          <small>Live platform snapshot</small>
        </div>
      </div>
    </div>

    <section v-if="quickStats.length" class="card-grid" aria-label="Quick entry points">
      <SummaryCard
        v-for="card in quickStats"
        :key="card.id"
        :data-testid="`quick-card-${card.id}`"
        :title="card.label"
        :value="card.value"
        :detail="card.delta"
        :to="quickCardRoutes[card.id]"
        :tone="card.id === 'devices' ? 'accent' : card.id === 'agents' ? 'blue' : card.id === 'jobs' ? 'green' : 'amber'"
      />
    </section>

    <section v-if="dashboard" class="content-grid">
      <article class="panel">
        <header class="panel-head">
          <h2>Today Summary</h2>
          <span>Operational snapshot</span>
        </header>
        <div class="summary-stack">
          <div v-for="item in todaySummary" :key="item.label" class="summary-item">
            <strong>{{ item.value }}</strong>
            <span>{{ item.label }}</span>
          </div>
        </div>
      </article>

      <article class="panel">
        <header class="panel-head">
          <h2>Live Activity</h2>
          <span>Recent signal flow</span>
        </header>
        <ActivityFeed :items="liveActivity" />
      </article>
    </section>

    <EmptyState
      v-if="!isLoading && loadError"
      title="Dashboard temporarily unavailable"
      :detail="loadError"
    />
  </section>
</template>

<style scoped>
.overview {
  display: grid;
  gap: 1.25rem;
}

.hero {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 1rem;
  padding: 1.5rem;
  border-radius: 32px;
  background:
    radial-gradient(circle at top right, rgba(124, 108, 255, 0.2), transparent 30%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 251, 255, 0.84));
  border: 1px solid rgba(91, 109, 145, 0.16);
  box-shadow: var(--shadow);
}

.hero-copy {
  display: grid;
  align-content: start;
  gap: 0.8rem;
}

.eyebrow {
  color: var(--accent-strong);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2.3rem, 4vw, 4.4rem);
  line-height: 0.95;
  letter-spacing: -0.06em;
}

.hero p {
  max-width: 36rem;
  margin: 0;
  color: var(--muted);
  font-size: 1.03rem;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 0.4rem;
}

.primary-action,
.secondary-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 3rem;
  padding: 0 1.15rem;
  border-radius: 999px;
  font-weight: 700;
}

.primary-action {
  background: linear-gradient(180deg, var(--accent), var(--accent-strong));
  color: white;
}

.secondary-action {
  background: rgba(124, 108, 255, 0.1);
  color: var(--accent-strong);
}

.hero-summary {
  display: grid;
  gap: 0.85rem;
  align-content: center;
}

.summary-line {
  padding: 1rem;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.66);
  border: 1px solid rgba(91, 109, 145, 0.12);
}

.summary-line span,
.summary-line small {
  display: block;
  color: var(--muted);
}

.summary-line strong {
  display: block;
  margin: 0.2rem 0;
  font-size: 1.5rem;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
}

.content-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

.summary-stack {
  display: grid;
  gap: 0.85rem;
}

.summary-item {
  display: grid;
  gap: 0.2rem;
  padding: 0.95rem 1rem;
  border-radius: 18px;
  background: rgba(124, 108, 255, 0.06);
}

.summary-item strong {
  font-size: 1.3rem;
}

.summary-item span {
  color: var(--muted);
}

@media (max-width: 1120px) {
  .hero,
  .content-grid {
    grid-template-columns: 1fr;
  }

  .card-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
