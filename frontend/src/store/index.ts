// UHAKIX Frontend Store — Zustand for state management

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// ── App State ──────────────────────────────────────────────
interface AppState {
  language: 'en' | 'sw' | 'mix';
  setLanguage: (lang: 'en' | 'sw' | 'mix') => void;
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      language: 'sw',
      setLanguage: (lang) => set({ language: lang }),
      searchQuery: '',
      setSearchQuery: (q) => set({ searchQuery: q }),
      activeTab: 'dashboard',
      setActiveTab: (tab) => set({ activeTab: tab }),
    }),
    { name: 'uhakix-storage' }
  )
);

// ── Election State ─────────────────────────────────────────
interface ElectionState {
  submissionStatus: 'idle' | 'uploading' | 'processing' | 'verified' | 'rejected';
  submissionResult: any;
  setSubmissionStatus: (status: ElectionState['submissionStatus']) => void;
  setSubmissionResult: (result: any) => void;
  resetSubmission: () => void;
}

export const useElectionStore = create<ElectionState>()(
  (set) => ({
    submissionStatus: 'idle',
    submissionResult: null,
    setSubmissionStatus: (status) => set({ submissionStatus: status }),
    setSubmissionResult: (result) => set({ submissionResult: result }),
    resetSubmission: () => set({ submissionStatus: 'idle', submissionResult: null }),
  })
);

// ── Directory State ────────────────────────────────────────
interface DirectoryState {
  selectedEntity: any;
  setSelectedEntity: (entity: any) => void;
  graphData: { nodes: any[]; edges: any[] };
  setGraphData: (data: { nodes: any[]; edges: any[] }) => void;
}

export const useDirectoryStore = create<DirectoryState>()(
  (set) => ({
    selectedEntity: null,
    setSelectedEntity: (entity) => set({ selectedEntity: entity }),
    graphData: { nodes: [], edges: [] },
    setGraphData: (data) => set({ graphData: data }),
  })
);
