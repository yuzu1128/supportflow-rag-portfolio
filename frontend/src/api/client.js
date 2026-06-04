import { mockDashboard, mockAskResponse } from '../data/mockData.js';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') ?? '';
const REQUEST_TIMEOUT_MS = 1600;

async function fetchJson(path, options = {}) {
  if (!API_BASE_URL) {
    throw new Error('VITE_API_BASE_URL is not configured');
  }

  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers ?? {}),
      },
      signal: controller.signal,
      ...options,
    });

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`);
    }

    return response.json();
  } finally {
    window.clearTimeout(timer);
  }
}

export async function loadDashboard() {
  try {
    const data = await fetchJson('/dashboard');
    return { ...mockDashboard, ...data, mode: 'backend' };
  } catch (error) {
    return {
      ...mockDashboard,
      mode: 'mock',
      backendWarning: error.message,
    };
  }
}

export async function askQuestion(question) {
  try {
    const data = await fetchJson('/ask', {
      method: 'POST',
      body: JSON.stringify({ question }),
    });
    return {
      ...data,
      mode: 'backend',
      citations: (data.citations ?? []).map((citation) => ({
        title: citation.title,
        snippet: citation.snippet,
        confidence: Number(citation.score ?? 0).toFixed(2),
      })),
      scores: [
        { label: 'Answer confidence', value: data.abstained ? 'Abstained' : 'Grounded' },
        {
          label: 'Retrieval score',
          value: Number(data.citations?.[0]?.score ?? 0).toFixed(2),
        },
        { label: 'Citation coverage', value: `${data.citations?.length ?? 0} sources` },
        { label: 'Abstention', value: data.abstained ? 'Triggered' : 'Not needed' },
      ],
    };
  } catch (error) {
    return {
      ...mockAskResponse(question),
      mode: 'mock',
      backendWarning: error.message,
    };
  }
}
