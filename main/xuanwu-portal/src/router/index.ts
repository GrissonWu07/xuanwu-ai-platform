import { defineComponent, h } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import AgentsPage from '@/pages/AgentsPage.vue'
import AIConfigProxyPage from '@/pages/AIConfigProxyPage.vue'
import AlertsPage from '@/pages/AlertsPage.vue'
import ChannelsGatewaysPage from '@/pages/ChannelsGatewaysPage.vue'
import DevicesPage from '@/pages/DevicesPage.vue'
import JobsPage from '@/pages/JobsPage.vue'
import OverviewPage from '@/pages/OverviewPage.vue'
import PhasePage from '@/pages/PhasePage.vue'
import SettingsPage from '@/pages/SettingsPage.vue'
import SignOutPage from '@/pages/SignOutPage.vue'
import TelemetryAlarmsPage from '@/pages/TelemetryAlarmsPage.vue'
import UsersRolesPage from '@/pages/UsersRolesPage.vue'

const makePhaseRoute = (config: any) =>
  defineComponent({
    name: `${config.title}Route`,
    setup: () => () => h(PhasePage, { ...config }),
  })

const placeholder = (title: string) =>
  makePhaseRoute({
    title,
    eyebrow: 'Profile destination',
    description: 'Placeholder page for Phase 2 work.',
    metrics: [
      { label: 'Status', value: 'Ready' },
      { label: 'Scope', value: 'Phase 2' },
      { label: 'Owner', value: 'Portal' },
    ],
    tableTitle: `${title} inventory`,
    tableColumns: ['Item', 'State'],
    tableRows: [
      ['Skeleton', 'Available'],
      ['Layout', 'Ready'],
    ],
    activityTitle: 'Recent changes',
    activity: [{ title: `${title} placeholder created`, meta: 'Now' }],
  })

export const routes = [
  { path: '/', redirect: '/overview' },
  { path: '/overview', component: OverviewPage },
  { path: '/devices', component: DevicesPage },
  { path: '/agents', component: AgentsPage },
  { path: '/jobs', component: JobsPage },
  { path: '/alerts', component: AlertsPage },
  { path: '/users-roles', component: UsersRolesPage },
  { path: '/channels-gateways', component: ChannelsGatewaysPage },
  { path: '/ai-config-proxy', component: AIConfigProxyPage },
  { path: '/telemetry-alarms', component: TelemetryAlarmsPage },
  { path: '/settings', component: SettingsPage },
  { path: '/sign-out', component: SignOutPage },
]

export const router = createRouter({
  history: createWebHistory(),
  routes: routes as any,
})
