export const primaryTabs = [
  { label: 'Overview', to: '/overview' },
  { label: 'Devices', to: '/devices' },
  { label: 'Agents', to: '/agents' },
  { label: 'Jobs', to: '/jobs' },
  { label: 'Alerts', to: '/alerts' },
]

export const profileMenuItems = [
  { label: 'Users & Roles', to: '/users-roles' },
  { label: 'Channels & Gateways', to: '/channels-gateways' },
  { label: 'AI Config Proxy', to: '/ai-config-proxy' },
  { label: 'Telemetry & Alarms', to: '/telemetry-alarms' },
  { label: 'Settings', to: '/settings' },
  { label: 'Sign out', to: '/sign-out' },
]

export const topStatusPills = [
  { label: 'Devices online', value: '128' },
  { label: 'Jobs healthy', value: '24/24' },
  { label: 'Proxy sync', value: 'Live' },
]

export const overviewCards = [
  { title: 'Devices', value: '128', detail: '94 bound, 34 waiting for claim', tone: 'accent' },
  { title: 'Agents', value: '42', detail: 'Proxy healthy, upstream sampled', tone: 'blue' },
  { title: 'Jobs', value: '24', detail: '3 queued, 21 success today', tone: 'green' },
  { title: 'Alerts', value: '6', detail: '2 active, 4 acknowledged', tone: 'amber' },
]

export const overviewSummary = [
  { label: 'Fleet coverage', value: '74%', hint: 'Devices reporting in' },
  { label: 'Median sync lag', value: '42s', hint: 'Across active channels' },
  { label: 'Open alerts', value: '2', hint: 'Needs attention now' },
]

export const overviewActivity = [
  { title: 'Device 8F-221 bound to Workshop Gateway', meta: '2 minutes ago' },
  { title: 'Daily job sync completed successfully', meta: '18 minutes ago' },
  { title: 'Telemetry spike acknowledged by operator', meta: '31 minutes ago' },
  { title: 'Agent proxy refreshed provider catalog', meta: '42 minutes ago' },
]

export const phasePages = {
  devices: {
    title: 'Devices',
    eyebrow: 'Phase 1 workstream',
    description: 'Inspect the fleet, filter by claim state, and review lifecycle and runtime ownership.',
    filters: ['Claim state', 'Binding status', 'Last seen', 'OTA'],
    highlights: [
      {
        title: 'Add device intake',
        fields: ['Device ID', 'Display name', 'Binding channel', 'Claim code'],
      },
      {
        title: 'Manual add device',
        fields: ['Device ID', 'Owner', 'Model', 'Runtime tags'],
      },
    ],
    metrics: [
      { label: 'Registered', value: '128' },
      { label: 'Claimed', value: '94' },
      { label: 'Offline', value: '8' },
    ],
    tableTitle: 'Device list',
    tableColumns: ['Device', 'Status', 'Owner', 'Runtime'],
    tableRows: [
      ['edge-01', 'Bound', 'Ops North', 'Healthy'],
      ['edge-02', 'Claim pending', 'Unassigned', 'Last seen 8m ago'],
      ['edge-03', 'Bound', 'Lab Group', 'Healthy'],
    ],
    activityTitle: 'Recent device events',
    activity: [
      { title: 'Claim request received for edge-02', meta: '4 minutes ago' },
      { title: 'OTA status refreshed for edge-01', meta: '12 minutes ago' },
    ],
  },
  agents: {
    title: 'Agents',
    eyebrow: 'Phase 1 workstream',
    description: 'Proxy Agent-domain resources and surface upstream health before deeper forms arrive.',
    filters: ['Template', 'Provider', 'Context', 'Sync health'],
    highlights: [
      {
        title: 'Role config',
        fields: ['Role key', 'Scope', 'Model access', 'Status'],
      },
      {
        title: 'Template and context',
        fields: ['Template name', 'Provider', 'Function mapping', 'Context provider'],
      },
    ],
    metrics: [
      { label: 'Proxy status', value: 'Healthy' },
      { label: 'Providers', value: '8' },
      { label: 'Models', value: '31' },
    ],
    tableTitle: 'Agent catalogue',
    tableColumns: ['Agent', 'Provider', 'Model', 'Sync'],
    tableRows: [
      ['assistant-core', 'OpenAI', 'gpt-5', 'Live'],
      ['ops-copilot', 'Anthropic', 'claude-sonnet', 'Live'],
      ['field-agent', 'Local proxy', 'fallback', 'Upstream degraded'],
    ],
    activityTitle: 'Proxy activity',
    activity: [
      { title: 'Provider catalog refreshed from XuanWu', meta: '7 minutes ago' },
      { title: 'Model sync delayed by upstream timeout', meta: '22 minutes ago' },
    ],
    upstream: {
      title: 'Upstream XuanWu unavailable',
      detail: 'Live data is still proxied through management APIs, so this section degrades to cached state when upstream is offline.',
    },
  },
  jobs: {
    title: 'Jobs',
    eyebrow: 'Phase 1 workstream',
    description: 'Review schedules, job runs, and scheduler health at a glance.',
    metrics: [
      { label: 'Schedules', value: '18' },
      { label: 'Queued', value: '3' },
      { label: 'Success today', value: '21' },
    ],
    tableTitle: 'Schedule list',
    tableColumns: ['Job', 'Schedule', 'Last run', 'State'],
    tableRows: [
      ['Telemetry rollup', '0 * * * *', '2 min ago', 'Success'],
      ['Device sync', '*/5 * * * *', '4 min ago', 'Queued'],
      ['Alert sweep', '*/10 * * * *', '8 min ago', 'Success'],
    ],
    activityTitle: 'Run history',
    activity: [
      { title: 'Device sync finished with 0 errors', meta: '2 minutes ago' },
      { title: 'Alert sweep queued for retry window', meta: '9 minutes ago' },
    ],
  },
  alerts: {
    title: 'Alerts',
    eyebrow: 'Phase 1 workstream',
    description: 'Track active alarms, severity, and operational follow-up without a noisy wall of cards.',
    metrics: [
      { label: 'Active', value: '2' },
      { label: 'Acknowledged', value: '4' },
      { label: 'Critical', value: '1' },
    ],
    tableTitle: 'Alert list',
    tableColumns: ['Alert', 'Severity', 'State', 'Source'],
    tableRows: [
      ['Gateway latency spike', 'High', 'Active', 'xuanwu-iot-gateway'],
      ['Device heartbeat lag', 'Medium', 'Acknowledged', 'xuanwu-device-gateway'],
      ['Proxy timeout', 'Critical', 'Active', 'XuanWu'],
    ],
    activityTitle: 'Operational signals',
    activity: [
      { title: 'Latency spike opened for gateway cluster', meta: '5 minutes ago' },
      { title: 'Heartbeat lag was acknowledged', meta: '19 minutes ago' },
    ],
  },
} as const
