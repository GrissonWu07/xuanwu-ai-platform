<script setup lang="ts">
import { ref } from 'vue'

import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { logout } from '@/api/management'

const isSubmitting = ref(false)
const isSignedOut = ref(false)
const error = ref('')

async function handleSignOut() {
  if (isSubmitting.value || isSignedOut.value) {
    return
  }

  isSubmitting.value = true
  error.value = ''

  try {
    await logout()
    isSignedOut.value = true
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to sign out'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="secondary-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Profile destination</span>
        <h1>Sign out</h1>
        <p>End the current local control-plane session without leaving the portal shell in an uncertain state.</p>
      </div>
    </header>

    <section class="metric-grid" aria-label="Sign out metrics">
      <SummaryCard title="Current action" :value="isSignedOut ? 'Signed out' : 'Ready'" detail="Local portal session state" />
      <SummaryCard title="Scope" value="Current operator" detail="Affects the active browser session" />
      <SummaryCard title="Backend" value="management" detail="POST /control-plane/v1/auth/logout" />
    </section>

    <div v-if="error">
      <EmptyState title="Sign out failed" :detail="error" />
    </div>

    <article v-else class="panel" data-testid="sign-out-panel">
      <header class="panel-head">
        <h2>Session control</h2>
        <span>{{ isSignedOut ? 'Completed' : 'Pending' }}</span>
      </header>

      <p class="panel-copy" v-if="!isSignedOut">
        Use this action when you want to hand the portal over to another operator or close the current authenticated session cleanly.
      </p>
      <p class="panel-copy" v-else>
        You have been signed out of the local control plane session.
      </p>

      <div class="actions">
        <button type="button" class="primary-action" :disabled="isSubmitting || isSignedOut" @click="handleSignOut">
          {{ isSignedOut ? 'Signed out' : isSubmitting ? 'Signing out...' : 'Sign out now' }}
        </button>
      </div>
    </article>
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
.panel-copy {
  margin: 0;
  color: var(--muted);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.panel {
  padding: 1.2rem;
  border-radius: 24px;
  background: var(--surface-strong);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-soft);
  display: grid;
  gap: 1rem;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 1rem;
}

.actions {
  display: flex;
  justify-content: flex-start;
}

.primary-action {
  min-height: 2.85rem;
  padding: 0 1.2rem;
  border-radius: 999px;
  font-weight: 700;
}

@media (max-width: 960px) {
  .page-head,
  .metric-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
