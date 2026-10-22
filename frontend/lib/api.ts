const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

export async function fetchFromApi(endpoint: string, options?: RequestInit) {
  // Only send Content-Type when there is a body; otherwise plain GETs trigger needless CORS preflights.
  const headers: Record<string, string> = {
    ...((options?.headers as Record<string, string>) || {}),
  };
  if (options?.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_URL}${endpoint}`, { ...options, headers });

  if (!res.ok) {
    const errText = await res.text().catch(() => res.statusText);
    // FastAPI errors look like {"detail": "..."}; show just the message.
    let message = errText;
    try {
      const parsed = JSON.parse(errText);
      if (typeof parsed?.detail === 'string') message = parsed.detail;
      else if (parsed?.detail) message = JSON.stringify(parsed.detail);
    } catch { /* not JSON, keep raw text */ }
    throw new Error(message || `API error (${res.status})`);
  }

  // DELETE / 204 responses have no body; res.json() would throw on them.
  if (res.status === 204) return null;
  const text = await res.text();
  return text ? JSON.parse(text) : null;
}

export interface ResourceItem {
  id: string;
  title: string;
  url: string;
  source: string;
  source_domain?: string;
  category: string;
  media_type: string;
  difficulty: string;
  tags: string[];
  summary?: string;
  published_at?: string;
  published_day?: string;
  read_time_min?: number;
  bookmark_count?: number;
  cluster_id?: number;
  cluster_slug?: string;
}

export interface PlanetNode {
  category_id: number;
  name: string;
  slug: string;
  description: string;
  color: string;
  resource_count: number;
  cx: number;
  cy: number;
  radius: number;
  top_terms: string[];
}

export interface GalaxyData {
  planets: PlanetNode[];
  edges: Array<{ from: string; to: string; strength: number }>;
}

export interface BookmarkPayload {
  resource_id: string;
  note?: string;
  saved_at?: string;
  client_id: string;
}

export interface CtfRoomPayload {
  challenge_name: string;
  description: string;
  difficulty: string;
  category: string;
  selected_tools: string[];
  expose_target_ui?: boolean;
}

export async function getGalaxy(): Promise<GalaxyData> {
  return fetchFromApi('/galaxy');
}

export async function getCategories() {
  return fetchFromApi('/categories');
}

export async function getResources(params?: {
  category?: string;
  q?: string;
  media_type?: string;
  source?: string;
  difficulty?: string;
  sort?: string;
  page?: number;
  page_size?: number;
}) {
  const searchParams = new URLSearchParams();
  if (params) {
    Object.entries(params).forEach(([key, val]) => {
      if (val !== undefined && val !== null && val !== '') {
        searchParams.append(key, String(val));
      }
    });
  }
  const query = searchParams.toString();
  return fetchFromApi(`/resources${query ? `?${query}` : ''}`);
}

export async function getResourceById(id: string) {
  return fetchFromApi(`/resources/${encodeURIComponent(id)}`);
}

export async function getPlanetDetail(slug: string) {
  return fetchFromApi(`/planets/${encodeURIComponent(slug)}`);
}

export async function getClusterStats() {
  return fetchFromApi('/clusters/stats');
}

export async function getStatsTimeseries(days: number = 30) {
  return fetchFromApi(`/stats/timeseries?days=${days}`);
}

export async function getStatsSources() {
  return fetchFromApi('/stats/sources');
}

export async function getLatestNewsletter() {
  return fetchFromApi('/newsletter/latest');
}

export async function getNewsletterArchive() {
  return fetchFromApi('/newsletter/archive');
}

export async function subscribeNewsletter(email: string) {
  return fetchFromApi('/subscribe', {
    method: 'POST',
    body: JSON.stringify({ email }),
  });
}

export async function getBookmarks(clientId: string) {
  return fetchFromApi(`/bookmarks/${encodeURIComponent(clientId)}`);
}

export async function syncBookmarks(clientId: string, bookmarks: BookmarkPayload[]) {
  return fetchFromApi('/bookmarks/sync', {
    method: 'POST',
    body: JSON.stringify({ client_id: clientId, bookmarks }),
  });
}

export async function triggerIngest() {
  return fetchFromApi('/ingest', { method: 'POST' });
}

// ---- CTF / Matrix lab -------------------------------------------------------

export async function createCtfRoom(payload: CtfRoomPayload) {
  return fetchFromApi('/agent/ctf-room', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

/** @deprecated use createCtfRoom */
export const createThmRoom = createCtfRoom;

/**
 * Submit a flag for a run. `taskIndex` is optional: the server matches the flag
 * to the right task when it is omitted.
 */
export async function submitCtfTaskFlag(
  clientId: string,
  runId: string,
  flag: string,
  taskIndex?: number
) {
  const body: Record<string, unknown> = { client_id: clientId, run_id: runId, flag };
  if (taskIndex !== undefined) body.task_index = taskIndex;
  return fetchFromApi('/agent/submit-task-flag', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

/** @deprecated use submitCtfTaskFlag */
export async function submitTaskFlag(clientId: string, runId: string, taskIndex: number, flag: string) {
  return submitCtfTaskFlag(clientId, runId, flag, taskIndex);
}

export async function getClientScore(clientId: string) {
  return fetchFromApi(`/agent/score/${encodeURIComponent(clientId)}`);
}

export async function getHint(runId: string, hintIndex: number, clientId: string) {
  return fetchFromApi(
    `/agent/hints/${encodeURIComponent(runId)}/${hintIndex}?client_id=${encodeURIComponent(clientId)}`
  );
}

export async function getLeaderboard(clientId?: string) {
  const q = clientId ? `?client_id=${encodeURIComponent(clientId)}` : '';
  return fetchFromApi(`/agent/leaderboard${q}`);
}

export async function getAgentRuns() {
  return fetchFromApi('/agent/runs');
}

export async function getAgentRunDetail(runId: string, clientId?: string) {
  const q = clientId ? `?client_id=${encodeURIComponent(clientId)}` : '';
  return fetchFromApi(`/agent/runs/${encodeURIComponent(runId)}${q}`);
}

export async function deleteAgentRun(runId: string) {
  return fetchFromApi(`/agent/runs/${encodeURIComponent(runId)}`, { method: 'DELETE' });
}

export async function getHarnessManifest() {
  return fetchFromApi('/agent/harness/manifest');
}

export async function getPublisherStats() {
  return fetchFromApi('/stats/publishers');
}

/**
 * The lab's target is BUILT from a Dockerfile + app code, not a pulled image,
 * so a single docker-compose.yml can't run it alone. This downloads the whole
 * workspace (Dockerfile, app/flag files, compose, README) as a zip.
 */
export async function downloadRunArchive(runId: string): Promise<Blob> {
  const res = await fetch(`${API_URL}/agent/runs/${encodeURIComponent(runId)}/download`);
  if (!res.ok) {
    const errText = await res.text().catch(() => res.statusText);
    throw new Error(`Download failed (${res.status}): ${errText}`);
  }
  return res.blob();
}