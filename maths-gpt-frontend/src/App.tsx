useEffect(() => {
  console.log("App mounted");
}, []);
// src/App.tsx
import React, { useEffect, useRef, useState } from "react";

type HistoryItem = { id: number; role: "user" | "assistant"; content: string };

export default function App(): JSX.Element {
  const [question, setQuestion] = useState<string>("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [model, setModel] = useState<string>("llama-3.3-70b-versatile");
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  async function askQuestion(e?: React.FormEvent) {
    e?.preventDefault();
    if (!question.trim()) return;
    setError(null);

    const q = question.trim();
    const entry: HistoryItem = { id: Date.now(), role: "user", content: q };
    setHistory((h) => [entry, ...h]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q, model }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Server error");
      const assistant: HistoryItem = { id: Date.now() + 1, role: "assistant", content: data.response };
      setHistory((h) => [assistant, ...h]);
    } catch (err: any) {
      setError(err?.message || "Unknown error");
      const fail: HistoryItem = { id: Date.now() + 2, role: "assistant", content: `Error: ${err?.message || "Unknown"}` };
      setHistory((h) => [fail, ...h]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      <div className="max-w-6xl mx-auto p-6">
        <header className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-pink-500 rounded-xl flex items-center justify-center text-2xl font-bold shadow-lg">
              M
            </div>
            <div>
              <h1 className="text-2xl font-semibold">MathsGPT</h1>
              <p className="text-sm text-slate-400">Ask math questions — SymPy + LLM powered</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button className="px-3 py-1.5 rounded-md border border-slate-700 text-sm hover:bg-slate-800">Settings</button>
            <div className="text-sm text-slate-400">Model:</div>
            <select value={model} onChange={(e) => setModel(e.target.value)} className="bg-slate-800 border border-slate-700 rounded-md px-2 py-1 text-sm">
              <option value="llama-3.3-70b-versatile">llama-3.3-70b-versatile</option>
              <option value="gemma2-7b">gemma2-7b (legacy)</option>
              <option value="gpt-lite-1b">gpt-lite-1b (local)</option>
            </select>
          </div>
        </header>

        <main className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <section className="md:col-span-3 bg-slate-800 rounded-2xl p-4 shadow">
            <div className="h-[60vh] overflow-auto mb-4 flex flex-col-reverse gap-3" aria-live="polite">
              {history.length === 0 && <div className="text-center text-slate-400 py-8">No interactions yet — ask a question below.</div>}
              {history.map((item) => (
                <div key={item.id} className={`p-4 rounded-lg max-w-xl ${item.role === "user" ? "bg-slate-700 self-end text-right" : "bg-slate-700/60 self-start"}`}>
                  <div className="text-sm text-slate-300 mb-1">{item.role === "user" ? "You" : "MathsGPT"}</div>
                  <div className="whitespace-pre-wrap">{item.content}</div>
                </div>
              ))}
            </div>

            <form onSubmit={(e) => askQuestion(e)} className="flex gap-3 items-center">
              <textarea ref={inputRef} value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Type a math question" className="flex-1 min-h-[56px] max-h-40 resize-none bg-slate-900 border border-slate-700 rounded-md p-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-600" />
              <div className="flex items-center gap-2">
                <button type="submit" disabled={loading} className="bg-indigo-600 px-4 py-2 rounded-md shadow hover:bg-indigo-500 disabled:opacity-60">
                  {loading ? "Thinking…" : "Find my answer"}
                </button>
              </div>
            </form>
            {error && <div className="mt-3 text-sm text-rose-400">{error}</div>}
          </section>

          <aside className="md:col-span-1 space-y-4">
            <div className="bg-slate-800 rounded-2xl p-4 shadow">
              <h3 className="text-sm text-slate-300 mb-2">Quick Actions</h3>
              <button onClick={() => { setQuestion("Solve x^2 - 5x + 6 = 0"); inputRef.current?.focus(); }} className="w-full text-left bg-slate-700/40 px-3 py-2 rounded-md text-sm mb-2">Try sample: quadratic</button>
              <button onClick={() => { setQuestion("Differentiate sin(x) with respect to x"); inputRef.current?.focus(); }} className="w-full text-left bg-slate-700/40 px-3 py-2 rounded-md text-sm">Try sample: calculus</button>
            </div>

            <div className="bg-slate-800 rounded-2xl p-4 shadow max-h-[40vh] overflow-auto">
              <h3 className="text-sm text-slate-300 mb-2">Recent</h3>
              <ul className="space-y-2 text-sm text-slate-400">
                {history.slice(0, 8).map((h) => (
                  <li key={h.id} className="truncate">
                    <button onClick={() => { setQuestion(h.content); inputRef.current?.focus(); }} className="w-full text-left">{h.content}</button>
                  </li>
                ))}
              </ul>
            </div>
          </aside>
        </main>

        <footer className="mt-8 text-xs text-slate-500 text-center">Made with ❤️ — MathsGPT</footer>
      </div>
    </div>
  );
}
