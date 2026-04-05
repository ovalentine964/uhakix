import React, { useState } from 'react';
import Head from 'next/head';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';

interface Entity {
  id: string;
  name: string;
  entity_type: string;
  total_value?: number;
  tender_count?: number;
}

interface Relationship {
  source: string;
  target: string;
  type: string;
  strength: number;
}

const SAMPLE_ENTITIES: Entity[] = [
  { id: 'comp_1', name: 'Omega Construction Ltd', entity_type: 'company', total_value: 2400000000, tender_count: 34 },
  { id: 'comp_2', name: 'Greenfield Supplies Co.', entity_type: 'company', total_value: 890000000, tender_count: 12 },
  { id: 'pol_1', name: 'Hon. James Mwangi', entity_type: 'politician', total_value: 0, tender_count: 0 },
  { id: 'pol_2', name: 'Sen. Amina Hassan', entity_type: 'politician', total_value: 0, tender_count: 0 },
  { id: 'comp_3', name: 'Eastland Engineering', entity_type: 'company', total_value: 1560000000, tender_count: 28 },
  { id: 'comp_4', name: 'Pioneer Logistics Ltd', entity_type: 'company', total_value: 340000000, tender_count: 6 },
];

const SAMPLE_RELATIONSHIPS: Relationship[] = [
  { source: 'pol_1', target: 'comp_1', type: 'contract_awarded', strength: 0.85 },
  { source: 'pol_1', target: 'comp_2', type: 'contract_awarded', strength: 0.45 },
  { source: 'comp_1', target: 'comp_3', type: 'shared_director', strength: 0.92 },
  { source: 'pol_2', target: 'comp_2', type: 'contract_awarded', strength: 0.67 },
  { source: 'comp_2', target: 'comp_4', type: 'shared_address', strength: 0.38 },
];

const ENTITY_COLORS: Record<string, string> = {
  politician: 'bg-purple-100 text-purple-800 border-purple-300',
  company: 'bg-blue-100 text-blue-800 border-blue-300',
  ministry: 'bg-green-100 text-green-800 border-green-300',
};

export default function Directory() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);
  const [filterType, setFilterType] = useState<string>('all');
  const [searchResults, setSearchResults] = useState<Entity[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = () => {
    const q = searchQuery.toLowerCase();
    if (!q) return;
    const results = SAMPLE_ENTITIES.filter(e => e.name.toLowerCase().includes(q));
    setSearchResults(results);
    setHasSearched(true);
  };

  const filteredEntities = filterType === 'all' ? searchResults : searchResults.filter(e => e.entity_type === filterType);

  return (
    <div className="min-h-screen bg-gray-50">
      <Head><title>Entity Directory — UHAKIX</title></Head>
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Entity Directory</h1>
        <p className="text-gray-600 mb-8">
          Search politicians, companies, and their connections. Build transparency graphs across government data.
        </p>

        {/* Search Bar */}
        <div className="bg-white rounded-xl shadow p-6 mb-8">
          <div className="flex gap-3">
            <input
              type="text"
              className="flex-1 rounded-lg border border-gray-300 px-4 py-3 text-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Search by entity name (politician, company, ministry...)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            />
            <button
              onClick={handleSearch}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Search
            </button>
          </div>
          <div className="flex gap-2 mt-3">
            {[
              { key: 'all', label: 'All' },
              { key: 'politician', label: 'Politicians' },
              { key: 'company', label: 'Companies' },
              { key: 'ministry', label: 'Ministries' },
            ].map(f => (
              <button
                key={f.key}
                onClick={() => { setFilterType(f.key); if (hasSearched) handleSearch(); }}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  filterType === f.key ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {/* Results */}
        {hasSearched && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Entity List */}
            <div className="lg:col-span-2">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                {filteredEntities.length} results for &ldquo;{searchQuery}&rdquo;
              </h2>
              <div className="space-y-3">
                {filteredEntities.map(entity => (
                  <div
                    key={entity.id}
                    onClick={() => setSelectedEntity(entity)}
                    className={`bg-white rounded-xl shadow p-4 cursor-pointer transition-all hover:shadow-md ${
                      selectedEntity?.id === entity.id ? 'ring-2 ring-blue-500' : ''
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="flex items-center gap-3">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${ENTITY_COLORS[entity.entity_type]}`}>
                            {entity.entity_type}
                          </span>
                          <h3 className="font-semibold text-gray-900">{entity.name}</h3>
                        </div>
                        {entity.entity_type === 'company' && (
                          <p className="text-sm text-gray-500 mt-1">
                            Tenders: {entity.tender_count} · Total value: KES {(entity.total_value! / 1e9).toFixed(2)}B
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Detail Panel */}
            <div className="lg:col-span-1">
              {selectedEntity ? (
                <div className="bg-white rounded-xl shadow p-6 sticky top-24">
                  <h2 className="text-xl font-bold text-gray-900 mb-2">{selectedEntity.name}</h2>
                  <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${ENTITY_COLORS[selectedEntity.entity_type]}`}>
                    {selectedEntity.entity_type}
                  </span>

                  <div className="mt-4 space-y-2">
                    {selectedEntity.entity_type === 'company' && (
                      <>
                        <InfoRow label="Tenders Won" value={selectedEntity.tender_count?.toString() || '0'} />
                        <InfoRow label="Total Value" value={`KES ${(selectedEntity.total_value! / 1e9).toFixed(2)}B`} />
                      </>
                    )}
                  </div>

                  <h3 className="font-semibold text-gray-900 mt-6 mb-3">Connections</h3>
                  <div className="space-y-2">
                    {SAMPLE_RELATIONSHIPS
                      .filter(r => r.source === selectedEntity.id || r.target === selectedEntity.id)
                      .map((rel, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm p-2 bg-gray-50 rounded">
                          <span className="font-medium">{rel.source === selectedEntity.id ? '→' : '←'}</span>
                          <span>{rel.type}</span>
                          <span className="ml-auto text-gray-400">{Math.round(rel.strength * 100)}%</span>
                        </div>
                      ))}
                  </div>

                  {/* Visualization placeholder */}
                  <div className="mt-4 h-48 bg-gray-100 rounded-lg flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <p className="text-3xl mb-1">🔗</p>
                      <p className="text-sm">Graph visualization</p>
                      <p className="text-xs text-gray-400">Neo4j force-directed graph</p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="bg-white rounded-xl shadow p-6 text-center text-gray-500">
                  <p className="text-4xl mb-3">🔍</p>
                  <p>Select an entity to view details and connections</p>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between text-sm py-1 border-b border-gray-100 last:border-0">
      <span className="text-gray-500">{label}</span>
      <span className="font-medium text-gray-900">{value}</span>
    </div>
  );
}
