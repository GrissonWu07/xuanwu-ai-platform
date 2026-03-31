export interface DashboardOverview {
  hero: {
    title: string
    subtitle: string
    primaryAction: string
    secondaryAction: string
  }
  statusPills: Array<{ label: string; value: string }>
  quickStats: Array<{ id: string; label: string; value: string; delta: string }>
  todaySummary: Array<{ label: string; value: string }>
  liveActivity: Array<{ id: string; title: string; detail: string; at: string }>
}

export interface DevicesCollectionResponse {
  items: Array<{
    device_id: string
    display_name?: string
    owner_user_id: string
    lifecycle_status: string
    bind_status: string
    device_type: string
    protocol_type: string
    last_seen_at?: string
  }>
}

export interface DeviceDetailResponse {
  device: {
    device_id: string
    display_name?: string
    owner_user_id: string
    lifecycle_status: string
    bind_status: string
    device_type: string
    protocol_type: string
    last_seen_at?: string
  }
  binding?: {
    agent_id?: string
    channel_id?: string
    model_config_id?: string
  }
  runtime?: {
    session_status?: string
    capability_route_count?: number
  }
  recent_events: Array<{ id: string; title: string; detail: string; at: string }>
  recent_telemetry: Array<{ metric: string; value: string; at: string }>
}

export interface JobsOverviewResponse {
  summary: Array<{ label: string; value: string }>
  schedules: Array<{
    schedule_id: string
    name: string
    executor_type: string
    schedule: string
    next_run_at?: string
    status: string
  }>
  runs: Array<{
    job_run_id: string
    schedule_id: string
    status: string
    executor_type: string
    started_at?: string
    finished_at?: string
  }>
}

export interface JobScheduleDetailResponse {
  schedule_id: string
  name?: string
  executor_type: string
  schedule?: string
  cron?: string
  timezone?: string
  next_run_at?: string
  status?: string
  payload?: Record<string, string | number | boolean | null | undefined>
}

export interface JobRunDetailResponse {
  job_run_id: string
  schedule_id: string
  status: string
  executor_type: string
  scheduled_for?: string
  started_at?: string
  finished_at?: string
  result?: {
    status?: string
    details?: Record<string, string | number | boolean | null | undefined>
  }
  error?: {
    code?: string
    message?: string
  }
}

export interface AlertsOverviewResponse {
  summary: Array<{ label: string; value: string }>
  alerts: Array<{
    alarm_id: string
    title: string
    severity: string
    status: string
    source: string
    created_at?: string
  }>
  activity: Array<{ id: string; title: string; detail: string; at: string }>
}

export interface AlarmDetailResponse {
  alarm_id: string
  title: string
  severity: string
  status: string
  source: string
  created_at?: string
  message?: string
  gateway_id?: string
  device_id?: string
}

export interface AgentListItem {
  agent_id: string
  name: string
  status: string
  provider_id?: string
  model_id?: string
  updated_at?: string
}

export interface ModelProviderItem {
  provider_id: string
  name: string
  provider_type: string
  status: string
  base_url?: string
}

export interface ModelConfigItem {
  model_id: string
  label: string
  model_name: string
  provider_id: string
  status: string
  capabilities?: string[]
}

export interface XuanwuListResponse<T> {
  items: T[]
}

export interface AuthMeResponse {
  user_id: string
  display_name: string
  avatar_url?: string
  email?: string
  role_ids: string[]
  permissions: string[]
}

export interface RoleItem {
  role_id: string
  label: string
  description?: string
  permissions?: string[]
  permission_count?: number
}

export interface UserItem {
  user_id: string
  display_name?: string
  email?: string
  status?: string
  role_ids?: string[]
}

export interface ChannelItem {
  channel_id: string
  display_name?: string
  owner_user_id?: string
  status?: string
  device_count?: number
}

export interface GatewayItem {
  gateway_id: string
  display_name?: string
  adapter_type?: string
  status?: string
  site_id?: string
}

export interface PortalConfigResponse {
  brand?: {
    product_name?: string
    support_email?: string
  }
  features?: Record<string, boolean>
  endpoints?: Record<string, string>
}

export interface EventItem {
  event_id: string
  event_type: string
  severity?: string
  device_id?: string
  gateway_id?: string
  occurred_at?: string
}

export interface TelemetryItem {
  telemetry_id: string
  device_id?: string
  capability_code: string
  value?: string | number | boolean
  reported_at?: string
}

declare global {
  interface Window {
    __XUANWU_PORTAL_API_BASE_URL__?: string
  }
}

function getApiBaseUrl() {
  const runtimeBaseUrl =
    typeof window !== 'undefined' ? window.__XUANWU_PORTAL_API_BASE_URL__?.replace(/\/$/, '') : undefined
  const buildTimeBaseUrl = ((import.meta as any).env?.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, '')
  return runtimeBaseUrl ?? buildTimeBaseUrl ?? ''
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    headers: {
      Accept: 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  })

  if (!response.ok) {
    const error = new Error(`Request failed for ${path}: ${response.status}`)
    ;(error as Error & { status?: number }).status = response.status
    throw error
  }

  return response.json() as Promise<T>
}

export function getDashboardOverview() {
  return requestJson<DashboardOverview>('/control-plane/v1/dashboard/overview')
}

export function getAuthMe() {
  return requestJson<AuthMeResponse>('/control-plane/v1/auth/me')
}

export function listRoles() {
  return requestJson<{ items: RoleItem[] }>('/control-plane/v1/roles')
}

export function listUsers() {
  return requestJson<{ items: UserItem[] }>('/control-plane/v1/users')
}

export function listChannels() {
  return requestJson<{ items: ChannelItem[] }>('/control-plane/v1/channels')
}

export function listGateways() {
  return requestJson<{ items: GatewayItem[] }>('/control-plane/v1/gateways')
}

export function getPortalConfig() {
  return requestJson<PortalConfigResponse>('/control-plane/v1/portal/config')
}

export function logout() {
  return requestJson<{ ok?: boolean }>('/control-plane/v1/auth/logout', {
    method: 'POST',
  })
}

export function getDevices() {
  return requestJson<DevicesCollectionResponse>('/control-plane/v1/devices')
}

export function getDeviceDetail(deviceId: string) {
  return requestJson<DeviceDetailResponse>(`/control-plane/v1/devices/${deviceId}/detail`)
}

export function getJobsOverview() {
  return requestJson<JobsOverviewResponse>('/control-plane/v1/jobs/overview')
}

export function getJobSchedule(scheduleId: string) {
  return requestJson<JobScheduleDetailResponse>(`/control-plane/v1/jobs/schedules/${scheduleId}`)
}

export function getJobRun(jobRunId: string) {
  return requestJson<JobRunDetailResponse>(`/control-plane/v1/jobs/runs/${jobRunId}`)
}

export function getAlertsOverview() {
  return requestJson<AlertsOverviewResponse>('/control-plane/v1/alerts/overview')
}

export function listAlarms() {
  return requestJson<{ items: AlertsOverviewResponse['alerts'] }>('/control-plane/v1/alarms')
}

export function getAlarm(alarmId: string) {
  return requestJson<AlarmDetailResponse>(`/control-plane/v1/alarms/${alarmId}`)
}

export function listEvents() {
  return requestJson<{ items: EventItem[] }>('/control-plane/v1/events')
}

export function listTelemetry() {
  return requestJson<{ items: TelemetryItem[] }>('/control-plane/v1/telemetry')
}

export function ackAlarm(alarmId: string) {
  return requestJson(`/control-plane/v1/alarms/${alarmId}:ack`, {
    method: 'POST',
  })
}

export function listAgents() {
  return requestJson<XuanwuListResponse<AgentListItem>>('/control-plane/v1/xuanwu/agents')
}

export function listModelProviders() {
  return requestJson<XuanwuListResponse<ModelProviderItem>>('/control-plane/v1/xuanwu/model-providers')
}

export function listModels() {
  return requestJson<XuanwuListResponse<ModelConfigItem>>('/control-plane/v1/xuanwu/models')
}
