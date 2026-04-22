/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { Bot, Users, Hash, CheckCircle, RefreshCw } from 'lucide-react';

interface BotStatus {
  status: string;
  users: number;
  totalNumbers: number;
  availableNumbers: number;
}

export default function App() {
  const [status, setStatus] = useState<BotStatus | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStatus = async () => {
    try {
      const res = await fetch('/api/status');
      if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
      const contentType = res.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Oops! We expected JSON but got something else.");
      }
      const data = await res.json();
      setStatus(data);
    } catch (err) {
      console.error("Failed to fetch status:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Update every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-indigo-500/30">
      {/* Mesh Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] rounded-full bg-indigo-500/10 blur-[120px]" />
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] rounded-full bg-blue-500/10 blur-[120px]" />
      </div>

      <main className="relative max-w-5xl mx-auto px-6 py-12">
        <header className="mb-12 flex items-center justify-between">
          <div>
            <motion.h1 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-4xl font-bold tracking-tight mb-2 bg-gradient-to-r from-indigo-400 to-blue-400 bg-clip-text text-transparent"
            >
              DXA Number Bot
            </motion.h1>
            <p className="text-slate-400">Real-time status and database monitoring dashboard.</p>
          </div>
          <motion.div 
            animate={{ rotate: loading ? 360 : 0 }}
            transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
            className="p-3 rounded-full bg-slate-900 border border-slate-800"
          >
            <Bot className="w-6 h-6 text-indigo-400" />
          </motion.div>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatusCard 
            icon={<Bot className="w-5 h-5" />}
            label="Bot Status"
            value={status?.status || 'Unknown'}
            color="text-emerald-400"
            delay={0.1}
          />
          <StatusCard 
            icon={<Users className="w-5 h-5" />}
            label="Total Users"
            value={status?.users.toString() || '0'}
            color="text-blue-400"
            delay={0.2}
          />
          <StatusCard 
            icon={<Hash className="w-5 h-5" />}
            label="Total Numbers"
            value={status?.totalNumbers.toString() || '0'}
            color="text-purple-400"
            delay={0.3}
          />
          <StatusCard 
            icon={<CheckCircle className="w-5 h-5" />}
            label="Available Stock"
            value={status?.availableNumbers.toString() || '0'}
            color="text-indigo-400"
            delay={0.4}
          />
        </section>

        <div className="p-8 rounded-3xl bg-slate-900/50 border border-slate-800 backdrop-blur-sm">
          <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
            <RefreshCw className="w-5 h-5 text-indigo-400" />
            Live Logs
          </h2>
          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-950 font-mono text-sm border border-slate-900 text-slate-400">
               <span className="text-indigo-500">[SYSTEM]</span> Bot logic initialized successfully using Node.js API.
            </div>
            <div className="p-4 rounded-xl bg-slate-950 font-mono text-sm border border-slate-900 text-slate-400">
               <span className="text-emerald-500">[STATUS]</span> Server running on port 3000.
            </div>
            <div className="p-4 rounded-xl bg-slate-950 font-mono text-sm border border-slate-900 text-slate-400">
               <span className="text-blue-500">[BOT]</span> Watching for commands... (10s cooldown enabled)
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function StatusCard({ icon, label, value, color, delay }: { icon: any, label: string, value: string, color: string, delay: number }) {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="p-6 rounded-3xl bg-slate-900/50 border border-slate-800 backdrop-blur-sm hover:border-slate-700 transition-colors"
    >
      <div className={`mb-4 p-2 w-fit rounded-lg bg-slate-950 ${color}`}>
        {icon}
      </div>
      <p className="text-slate-400 text-sm mb-1">{label}</p>
      <p className="text-2xl font-bold">{value}</p>
    </motion.div>
  );
}
