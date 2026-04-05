"use client";
import React, { useState, useCallback, useRef } from 'react';
import Header from '../components/layout/Header';
import Footer from '../components/layout/Footer';
import { VoiceRecorder } from '../components/voice/VoiceRecorder';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [messages, setMessages] = useState<{role: string, text: string, timestamp: string}[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [showVoiceModal, setShowVoiceModal] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    
    setUserInput('');
    setIsLoading(true);
    
    // Add user message
    const userMessage = { role: 'user', text, timestamp: new Date().toLocaleTimeString() };
    setMessages(prev => [...prev, userMessage]);
    
    try {
      // Call UHAKIX API
      const response = await fetch('/api/v1/citizen/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text, voice_response: voiceEnabled })
      });
      
      const data = await response.json();
      const uhakixMessage = { 
        role: 'uhakix', 
        text: data.answer || 'Asante! I found information about your question.', 
        timestamp: new Date().toLocaleTimeString() 
      };
      
      setMessages(prev => [...prev, uhakixMessage]);
      
      // Play audio response if enabled
      if (voiceEnabled && data.audio_url) {
        const audio = new Audio(data.audio_url);
        await audio.play();
      }
    } catch (error) {
      const errorMsg = { role: 'uhakix', text: '⚠️ Samahani! There was an error processing your request. Please try again.', timestamp: new Date().toLocaleTimeString() };
      setMessages(prev => [...prev, errorMsg]);
    }
    
    setIsLoading(false);
    scrollToBottom();
  };

  const quickActions = [
    { label: '💰 County Budget', q: 'Where is my county\'s budget money going?' },
    { label: '📋 Tender Info', q: 'How do I check if a tender was legitimate?' },
    { label: '📚 Constitution', q: 'What are my rights as a citizen?' },
    { label: '🗳️ Election', q: 'How can I verify election results?' },
    { label: '⚠️ Corruption', q: 'How do I spot political manipulation?' },
    { label: '💬 Speak', q: 'open-voice' },
  ];

  const stats = [
    { label: 'Counties Monitored', value: '47', color: 'text-blue-400' },
    { label: 'Contracts Tracked', value: '1,247', color: 'text-green-400' },
    { label: 'Citizen Questions', value: '12,456', color: 'text-purple-400' },
    { label: 'Voice Responses', value: '8,921', color: 'text-yellow-400' },
  ];

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <Header />
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        {/* Page Header */}
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold">📊 UHAKIX Dashboard</h1>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-green-400 text-sm font-medium">System Online</span>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {stats.map((stat) => (
            <div key={stat.label} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <p className="text-gray-400 text-xs font-medium">{stat.label}</p>
              <p className={`text-2xl font-bold mt-1 ${stat.color}`}>{stat.value}</p>
            </div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 bg-gray-900 p-1 rounded-xl">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'chat', label: '🦁 Ask UHAKIX' },
            { id: 'civic', label: '📚 Civic Ed' },
            { id: 'election', label: '🗳️ Elections' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-2 px-4 rounded-lg font-medium transition-all ${
                activeTab === tab.id ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Budget Section */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4">💰 Government Spending</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="font-semibold">National Government</h3>
                  <p className="text-2xl font-bold mt-2">KES 3.2T</p>
                  <p className="text-green-400 text-sm mt-1">Budget Allocated</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="font-semibold">County Governments</h3>
                  <p className="text-2xl font-bold mt-2">KES 361B</p>
                  <p className="text-yellow-400 text-sm mt-1">47 Counties</p>
                </div>
                <div className="bg-gray-800 p-4 rounded-lg">
                  <h3 className="font-semibold">Projects Tracked</h3>
                  <p className="text-2xl font-bold mt-2">1,247</p>
                  <p className="text-blue-400 text-sm mt-1">Under Monitoring</p>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4">🦁 Try Asking UHAKIX</h2>
              <div className="flex flex-wrap gap-3">
                {quickActions.map((action) => (
                  <button
                    key={action.label}
                    onClick={() => {
                      if (action.q === 'open-voice') {
                        setShowVoiceModal(true);
                      } else {
                        setActiveTab('chat');
                        sendMessage(action.q);
                      }
                    }}
                    className="px-4 py-2 bg-gray-800 hover:bg-blue-600 rounded-full text-sm transition-colors"
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="flex flex-col h-[600px] bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12 text-gray-400">
                  <div className="text-6xl mb-4">🦁</div>
                  <h3 className="text-xl font-bold text-white mb-2">Ask UHAKIX Anything</h3>
                  <p className="text-sm">Ask about budgets, tenders, your rights, elections, and more</p>
                  <p className="text-xs mt-2 text-blue-400">Voice, text, Sheng, or Kiswahili — we understand all</p>
                </div>
              )}
              
              {messages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-4 rounded-2xl ${
                    msg.role === 'user' 
                      ? 'bg-blue-600 text-white rounded-tr-none' 
                      : 'bg-gray-800 text-white rounded-tl-none'
                  }`}>
                    <div className="flex items-start gap-3">
                      {msg.role === 'uhakix' && <span className="text-2xl">🦁</span>}
                      <div className="flex-1">
                        <p className="text-sm leading-relaxed">{msg.text}</p>
                        <p className="text-xs opacity-60 mt-2">{msg.timestamp}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
              
              {isLoading && (
                <div className="flex justify-start">
                  <div className="bg-gray-800 p-4 rounded-2xl rounded-tl-none">
                    <span className="text-2xl">🦁</span>
                    <div className="flex gap-2 mt-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t border-gray-800">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setShowVoiceModal(true)}
                  className="p-3 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
                  title="Speak your question"
                >
                  🎤
                </button>
                <button
                  onClick={() => setVoiceEnabled(!voiceEnabled)}
                  className={`p-3 rounded-lg transition-colors ${
                    voiceEnabled ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-800 hover:bg-gray-700'
                  }`}
                  title={voiceEnabled ? 'Voice responses ON' : 'Voice responses OFF'}
                >
                  {voiceEnabled ? '🔊' : '🔇'}
                </button>
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendMessage(userInput)}
                  placeholder="Ask about government spending, your rights..."
                  className="flex-1 bg-gray-800 px-4 py-3 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  onClick={() => sendMessage(userInput)}
                  disabled={isLoading}
                  className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg text-sm font-medium"
                >
                  ➤
                </button>
              </div>
              
              {/* Quick actions */}
              <div className="flex gap-2 mt-2 overflow-x-auto">
                {['County budget', 'My rights', 'Election verify', 'Spot lies', 'Tender check'].map((q) => (
                  <button
                    key={q}
                    onClick={() => sendMessage(`Tell me about ${q.toLowerCase()}`)}
                    className="px-3 py-1 bg-gray-800 hover:bg-gray-700 rounded-full text-xs text-gray-300 whitespace-nowrap"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'civic' && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4">📜 Constitution of Kenya 2010</h2>
              <div className="space-y-3">
                {[
                  { art: 'Art 35', title: 'Access to Information', desc: 'Right to access information held by the State' },
                  { art: 'Art 43', title: 'Economic & Social Rights', desc: 'Right to health care, education, housing, food, water' },
                  { art: 'Art 47', title: 'Fair Administrative Action', desc: 'Administrative action must be fair and efficient' },
                  { art: 'Art 201', title: 'Public Finance', desc: 'Openness, accountability, public participation' },
                  { art: "Art 73-77", title: 'Leadership Integrity', desc: 'State officers must act with integrity' },
                ].map((item) => (
                  <div key={item.art} className="bg-gray-800 p-4 rounded-lg hover:bg-gray-700 transition-colors cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="px-3 py-1 bg-blue-600 text-white text-xs font-bold rounded-full">{item.art}</span>
                      <div>
                        <h3 className="font-semibold">{item.title}</h3>
                        <p className="text-sm text-gray-400 mt-1">{item.desc}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gray-900 border border-red-800/50 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4">⚠️ 48 Laws of Political Power</h2>
              <p className="text-gray-400 text-sm mb-4">How politicians manipulate citizens and what YOU can do about it</p>
              <div className="space-y-3">
                {[
                  { law: 'Law 3', title: 'Vague Promises', tactic: 'Politician says "I\'ll create jobs" with no plan/budget', action: 'Ask for specific commitments with deadlines' },
                  { law: 'Law 8', title: 'Campaign Bribery', tactic: '"Gifts" of maize/cash during campaigns', action: 'This is YOUR tax money, not their generosity' },
                  { law: 'Law 27', title: 'Ethnic Division', tactic: '"My tribe deserves to eat"', action: 'Demand policies for ALL Kenyans, not just their tribe' },
                ].map((item) => (
                  <div key={item.law} className="bg-gray-800 p-4 rounded-lg">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-red-600 text-white text-xs font-bold rounded">{item.law}</span>
                      <h3 className="font-semibold">{item.title}</h3>
                    </div>
                    <p className="text-sm text-red-400 mt-2">🔴 {item.tactic}</p>
                    <p className="text-sm text-green-400 mt-1">✅ {item.action}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'election' && (
          <div className="space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4">🗳️ Election Verification</h2>
              <p className="text-gray-400 mb-4">Upload a photo of Form 34A to verify the results</p>
              <div className="border-2 border-dashed border-gray-700 rounded-xl p-12 text-center hover:border-blue-500 transition-colors cursor-pointer">
                <div className="text-6xl mb-4">📷</div>
                <h3 className="text-lg font-semibold mb-2">Upload Form 34A Photo</h3>
                <p className="text-sm text-gray-400">Take a photo of the results posted outside your polling station</p>
                <p className="text-xs text-gray-500 mt-2">Supports: JPG, PNG, HEIC • Max: 10MB</p>
              </div>
              <button className="mt-4 w-full py-3 bg-blue-600 hover:bg-blue-700 rounded-lg font-medium transition-colors">
                Upload & Verify →
              </button>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h2 className="text-xl font-bold mb-4">🔊 Voice Verification</h2>
              <p className="text-gray-400 mb-4">Call the results hotline or send a voice message</p>
              <div className="flex items-center gap-4">
                <div className="flex-1 bg-gray-800 p-4 rounded-lg">
                  <h3 className="font-semibold">📞 Call: 0700 UHAKIX</h3>
                  <p className="text-sm text-gray-400 mt-1">Free from all networks in Kenya</p>
                </div>
                <div className="flex-1 bg-gray-800 p-4 rounded-lg">
                  <h3 className="font-semibold">🎤 Voice Note</h3>
                  <p className="text-sm text-gray-400 mt-1">Send voice via Telegram/WhatsApp</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Voice Modal */}
        {showVoiceModal && <VoiceRecorder onVoiceSubmit={(audioBlob) => {
          setMessages(prev => [...prev, { role: 'user', text: '[Voice message sent]', timestamp: new Date().toLocaleTimeString() }]);
          setShowVoiceModal(false);
        }} onClose={() => setShowVoiceModal(false)} />}
      </main>
      <Footer />
    </div>
  );
}
