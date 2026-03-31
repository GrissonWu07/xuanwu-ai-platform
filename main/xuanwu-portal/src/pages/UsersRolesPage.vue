<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import DataTable, { type DataTableColumn } from '@/components/DataTable.vue'
import EmptyState from '@/components/EmptyState.vue'
import SummaryCard from '@/components/SummaryCard.vue'
import { getAuthMe, listRoles, listUsers, type AuthMeResponse, type RoleItem, type UserItem } from '@/api/management'

const loading = ref(true)
const me = ref<AuthMeResponse | null>(null)
const roles = ref<RoleItem[]>([])
const users = ref<UserItem[]>([])
const error = ref('')

const roleColumns: DataTableColumn[] = [
  { key: 'label', label: 'Role' },
  { key: 'permission_count', label: 'Permissions' },
  { key: 'description', label: 'Description' },
]

const userColumns: DataTableColumn[] = [
  { key: 'display_name', label: 'User' },
  { key: 'email', label: 'Email' },
  { key: 'status', label: 'Status' },
  { key: 'roles', label: 'Roles' },
]

const roleRows = computed(() =>
  roles.value.map((role) => ({
    id: role.role_id,
    label: role.label,
    permission_count: String(role.permission_count ?? role.permissions?.length ?? 0),
    description: role.description ?? 'No description',
  })),
)

const userRows = computed(() =>
  users.value.map((user) => ({
    id: user.user_id,
    display_name: user.display_name ?? user.user_id,
    email: user.email ?? 'No email',
    status: user.status ?? 'unknown',
    roles: (user.role_ids ?? []).join(', ') || 'No roles',
  })),
)

async function loadUsersRoles() {
  loading.value = true
  error.value = ''

  try {
    const [mePayload, rolesPayload, usersPayload] = await Promise.all([getAuthMe(), listRoles(), listUsers()])
    me.value = mePayload
    roles.value = rolesPayload.items
    users.value = usersPayload.items
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Unable to load users and roles'
  } finally {
    loading.value = false
  }
}

onMounted(loadUsersRoles)
</script>

<template>
  <section class="secondary-page">
    <header class="page-head">
      <div>
        <span class="eyebrow">Profile destination</span>
        <h1>Users &amp; Roles</h1>
        <p>Review who owns the fleet, which roles exist, and what permissions are exposed through the management surface.</p>
      </div>
      <button type="button" class="ghost-action" @click="loadUsersRoles">Refresh</button>
    </header>

    <div v-if="error">
      <EmptyState title="Users & Roles unavailable" :detail="error" />
    </div>

    <template v-else>
      <section class="metric-grid" aria-label="Users and roles metrics">
        <SummaryCard title="Signed in user" :value="me?.display_name ?? 'Unknown'" :detail="me?.email ?? 'No email'" />
        <SummaryCard title="Users" :value="String(users.length)" detail="Managed by xuanwu-management-server" />
        <SummaryCard title="Roles" :value="String(roles.length)" detail="Effective permission groups" />
      </section>

      <article v-if="me" class="panel">
        <header class="panel-head">
          <h2>Current profile</h2>
          <span>{{ me.user_id }}</span>
        </header>
        <p class="profile-copy">
          {{ me.display_name }} currently holds
          <strong>{{ me.role_ids.length }}</strong>
          role assignments and
          <strong>{{ me.permissions.length }}</strong>
          effective permissions.
        </p>
      </article>

      <div v-if="loading" class="loading-copy">Loading users and roles...</div>

      <section v-else class="table-grid">
        <DataTable title="Role catalogue" :columns="roleColumns" :rows="roleRows" row-key="id" />
        <DataTable title="User directory" :columns="userColumns" :rows="userRows" row-key="id" />
      </section>
    </template>
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
.profile-copy,
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

.metric-grid,
.table-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.table-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
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
  margin-bottom: 0.75rem;
}

@media (max-width: 960px) {
  .page-head,
  .metric-grid,
  .table-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
