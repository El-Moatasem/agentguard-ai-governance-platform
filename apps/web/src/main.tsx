import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { apiGet, apiPost } from "./api";
import "./styles.css";

type Metrics = { agents: number; policies: number; audit_events: number; pending_approvals: number };

type Decision = { decision: string; reason: string; action_request_id?: number; approval_id?: number };

function App() {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [agents, setAgents] = useState<any[]>([]);
  const [policies, setPolicies] = useState<any[]>([]);
  const [approvals, setApprovals] = useState<any[]>([]);
  const [audits, setAudits] = useState<any[]>([]);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [error, setError] = useState<string>("");

  async function load() {
    try {
      const [m, a, p, ap, au] = await Promise.all([
        apiGet("/dashboard/metrics"),
        apiGet("/agents"),
        apiGet("/policies"),
        apiGet("/approvals"),
        apiGet("/audit-events"),
      ]);
      setMetrics(m); setAgents(a); setPolicies(p); setApprovals(ap); setAudits(au);
    } catch (e: any) { setError(e.message); }
  }

  useEffect(() => { load(); }, []);

  async function simulate(resource_name: string, action: string, environment = "sandbox") {
    setError("");
    try {
      const result = await apiPost("/decisions/evaluate", {
        agent_name: "customer-support-agent",
        user_email: "developer@demo.local",
        action,
        resource_name,
        environment,
        context: { customer_id: "C-10045", country: "Kenya" }
      });
      setDecision(result);
      await load();
    } catch (e: any) { setError(e.message); }
  }

  async function approve(id: number) {
    await apiPost(`/approvals/${id}/approve`, { notes: "Approved in demo workflow." });
    await load();
  }

  return <main>
    <header className="hero">
      <p className="eyebrow">MSSE Capstone MVP</p>
      <h1>AgentGuard</h1>
      <p>Govern AI agents with deterministic policies, human approval workflows, and searchable audit logs.</p>
    </header>

    {error && <section className="error">{error}</section>}

    <section className="metrics">
      {metrics && Object.entries(metrics).map(([key, value]) => <article key={key}><strong>{value}</strong><span>{key.replace("_", " ")}</span></article>)}
    </section>

    <section className="grid">
      <article>
        <h2>Decision Simulator</h2>
        <p>Run realistic agent actions and inspect the policy outcome.</p>
        <div className="buttonRow">
          <button onClick={() => simulate("customer_profile", "read")}>Allow profile read</button>
          <button onClick={() => simulate("customer_transactions", "read")}>Require approval</button>
          <button onClick={() => simulate("customer_profile", "read", "production")}>Deny production</button>
        </div>
        {decision && <pre>{JSON.stringify(decision, null, 2)}</pre>}
      </article>

      <article>
        <h2>Agents</h2>
        <ul>{agents.map(a => <li key={a.id}><b>{a.name}</b> — {a.risk_level}</li>)}</ul>
      </article>

      <article>
        <h2>Policies</h2>
        <ul>{policies.slice(0, 4).map(p => <li key={p.id}><b>{p.effect}</b> — {p.name}</li>)}</ul>
      </article>

      <article>
        <h2>Approvals</h2>
        <ul>{approvals.slice(0, 5).map(a => <li key={a.id}>#{a.id} — {a.status} {a.status === "pending" && <button onClick={() => approve(a.id)}>Approve</button>}</li>)}</ul>
      </article>
    </section>

    <section>
      <h2>Audit Events</h2>
      <div className="auditList">{audits.slice(0, 8).map(a => <div key={a.id}><b>{a.result}</b> {a.message}<small>{new Date(a.created_at).toLocaleString()}</small></div>)}</div>
    </section>
  </main>;
}

createRoot(document.getElementById("root")!).render(<App />);
