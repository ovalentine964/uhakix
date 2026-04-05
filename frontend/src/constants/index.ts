// UHAKIX Constants

// Kenyan Counties (47) — as objects with code+name
export const KENYAN_COUNTIES_WITH_CODES = [
  { code: "001", name: "Mombasa" }, { code: "002", name: "Kwale" },
  { code: "003", name: "Kilifi" }, { code: "004", name: "Tana River" },
  { code: "005", name: "Lamu" }, { code: "006", name: "Taita-Taveta" },
  { code: "007", name: "Garissa" }, { code: "008", name: "Wajir" },
  { code: "009", name: "Mandera" }, { code: "010", name: "Marsabit" },
  { code: "011", name: "Isiolo" }, { code: "012", name: "Meru" },
  { code: "013", name: "Tharaka-Nithi" }, { code: "014", name: "Embu" },
  { code: "015", name: "Kitui" }, { code: "016", name: "Machakos" },
  { code: "017", name: "Makueni" }, { code: "018", name: "Nyandarua" },
  { code: "019", name: "Nyeri" }, { code: "020", name: "Kirinyaga" },
  { code: "021", name: "Murang'a" }, { code: "022", name: "Kiambu" },
  { code: "023", name: "Turkana" }, { code: "024", name: "West Pokot" },
  { code: "025", name: "Samburu" }, { code: "026", name: "Trans-Nzoia" },
  { code: "027", name: "Uasin Gishu" }, { code: "028", name: "Elgeyo-Marakwet" },
  { code: "029", name: "Nandi" }, { code: "030", name: "Baringo" },
  { code: "031", name: "Laikipia" }, { code: "032", name: "Nakuru" },
  { code: "033", name: "Narok" }, { code: "034", name: "Kajiado" },
  { code: "035", name: "Kericho" }, { code: "036", name: "Bomet" },
  { code: "037", name: "Kakamega" }, { code: "038", name: "Vihiga" },
  { code: "039", name: "Bungoma" }, { code: "040", name: "Busia" },
  { code: "041", name: "Siaya" }, { code: "042", name: "Kisumu" },
  { code: "043", name: "Homa Bay" }, { code: "044", name: "Migori" },
  { code: "045", name: "Kisii" }, { code: "046", name: "Nyamira" },
  { code: "047", name: "Nairobi" },
] as const;

// Flat string array for simple dropdowns/maps
export const KENYAN_COUNTIES = KENYAN_COUNTIES_WITH_CODES.map(c => c.name) as string[];

// Presidential Candidates (sample)
export const PRESIDENTIAL_CANDIDATES = [
  "William Ruto", "Raila Odinga", "David Mwaure", "Ekuru Aukot", "George Wajackoyah"
] as const;

// API Endpoints
export const API_ENDPOINTS = {
  health: "/api/v1/health",
  transactions: "/api/v1/transactions",
  entities: "/api/v1/entities",
  budget: "/api/v1/budget",
  tenders: "/api/v1/tenders",
  anomalies: "/api/v1/anomalies",
  electionSubmit: "/api/v1/election/form34a/submit",
  electionResults: "/api/v1/election/results/national",
  electionAlerts: "/api/v1/election/alerts",
  directorySearch: "/api/v1/directory/search",
  citizenAsk: "/api/v1/citizen/ask",
} as const;

// Agent info for display
export const AGENT_INFO = {
  JASIRI: { name: "JASIRI", role: "Budget Intelligence", color: "#22c55e", icon: "💰" },
  RIFT: { name: "RIFT", role: "Procurement Analysis", color: "#3b82f6", icon: "🔍" },
  SCOUT: { name: "SCOUT", role: "Network Mapping", color: "#8b5cf6", icon: "🕸️" },
  SPHINX: { name: "SPHINX", role: "Anomaly Detection", color: "#ef4444", icon: "🧩" },
  KAZI: { name: "KAZI", role: "Task Orchestrator", color: "#f59e0b", icon: "⚡" },
  HERALD: { name: "HERALD", role: "Citizen Communication", color: "#06b6d4", icon: "📢" },
  SHIELD: { name: "SHIELD", role: "Legal Compliance", color: "#14b8a6", icon: "🛡️" },
  VIGIL: { name: "VIGIL", role: "Audit Trail", color: "#6366f1", icon: "👁️" },
  ATLAS: { name: "ATLAS", role: "Geographic Analysis", color: "#ec4899", icon: "🗺️" },
  LEDGER: { name: "LEDGER", role: "Blockchain Sync", color: "#f97316", icon: "⛓️" },
} as const;
