// UHAKIX API Client — Centralized HTTP client with auth and error handling

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor — add auth token if available
api.interceptors.request.use((config) => {
  const token = typeof window !== 'undefined'
    ? localStorage.getItem('ujuzio_token')
    : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor — global error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 429) {
      console.warn('Rate limited — UHAKIX API is protecting against abuse.');
    }
    if (error.response?.status === 403) {
      console.error('Access denied — SHIELD compliance layer blocked this request.');
    }
    return Promise.reject(error);
  }
);

// ── API Methods ─────────────────────────────────────────────

export const transparencyApi = {
  // Transactions
  getTransactions: (params: Record<string, any>) =>
    api.get('/transactions', { params }),

  getTransaction: (id: string) =>
    api.get(`/transactions/${id}`),

  // Entities
  getEntityConnections: (entityId: string) =>
    api.get(`/entities/${entityId}/connections`),

  getEntityProfile: (entityId: string) =>
    api.get(`/entities/${entityId}/profile`),

  searchEntities: (params: Record<string, any>) =>
    api.get('/directory/search', { params }),

  getEntityRelationships: (entityId: string, params?: Record<string, any>) =>
    api.get(`/directory/${entityId}/relationships`, { params }),

  // Budget
  getBudgetVariance: (ministry: string, fiscalYear?: string) =>
    api.get(`/budget/${ministry}/variance`, { params: { fiscal_year: fiscalYear } }),

  getCountyBudget: (countyCode: string, fiscalYear?: string) =>
    api.get(`/county/${countyCode}/budget`, { params: { fiscal_year: fiscalYear } }),

  // Tenders
  searchTenders: (params: Record<string, any>) =>
    api.get('/tenders', { params }),

  getTender: (id: string) =>
    api.get(`/tenders/${id}`),

  // Anomalies
  getAnomalies: (params: Record<string, any>) =>
    api.get('/anomalies', { params }),
};

export const electionApi = {
  // Form 34A
  submitForm34A: async (file: File, submitterName?: string, stationCode?: string) => {
    const formData = new FormData();
    formData.append('photo', file);
    if (submitterName) formData.append('submitter_name', submitterName);
    if (stationCode) formData.append('station_code', stationCode);

    return api.post('/election/form34a/submit', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  getSubmissionStatus: (submissionId: string) =>
    api.get(`/election/form34a/${submissionId}`),

  // Results
  getConstituencyResults: (name: string) =>
    api.get(`/election/results/constituency/${name}`),

  getCountyResults: (name: string) =>
    api.get(`/election/results/county/${name}`),

  getNationalResults: () =>
    api.get('/election/results/national'),

  // Alerts
  getAlerts: (params?: Record<string, any>) =>
    api.get('/election/alerts', { params }),

  // Stations
  searchStations: (params: Record<string, any>) =>
    api.get('/election/stations', { params }),

  getStationForms: (stationCode: string) =>
    api.get(`/election/stations/${stationCode}/forms`),
};

export const citizenApi = {
  askQuestion: (question: string, language = 'sw', channel = 'web') =>
    api.post('/citizen/ask', { question, language, channel }),

  getReportStatus: (reportId: string) =>
    api.get(`/citizen/report/${reportId}`),
};

export const agentsApi = {
  listAgents: () =>
    api.get('/agents/'),

  getAgent: (name: string) =>
    api.get(`/agents/${name}`),

  queryAgents: (query: string, agent?: string) =>
    api.post('/agents/query', { query, agent }),
};

export default api;
