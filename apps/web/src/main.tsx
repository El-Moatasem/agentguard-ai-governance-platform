import React, { FormEvent, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { apiDownload, apiGet, apiPost, DemoRole, demoTokens, getToken, setDemoRole } from "./api";
import "./styles.css";

type Metrics = {
  agents: number;
  policies: number;
  active_policies: number;
  audit_events: number;
  pending_approvals: number;
  tool_executions: number;
  decisions: { allow: number; deny: number; requires_approval: number };
};

type Agent = { id: number; name: string; purpose: string; risk_level: string; status: string };
type Policy = { id: number; name: string; description: string; effect: "allow" | "deny" | "requires_approval"; priority: number; active: boolean; version: number; conditions: Record<string, unknown> };
type Approval = { id: number; action_request_id: number; status: string; reviewer_email?: string | null; reviewer_notes: string; expires_at?: string | null; created_at: string };
type AuditEvent = { id: number; correlation_id?: string | null; actor_email: string; event_type: string; result: string; message: string; created_at: string };
type Execution = { id: number; action_request_id: number; provider: string; tool_name: string; status: string; idempotency_key: string; attempt_count: number; response_data: Record<string, unknown>; error_message: string; created_at: string };
type Decision = { correlation_id: string; decision: string; reason: string; matched_policy_id?: number; matched_policy_name?: string; evaluated_policy_count: number; action_request_id?: number; approval_id?: number };
type GovernedExecution = { correlation_id: string; decision: string; reason: string; action_request_id: number; approval_id?: number | null; execution: Execution };
type AgentRun = { provider: string; plan: { tool_name: string; action: string; resource_name: string; arguments: Record<string, unknown>; rationale: string }; governance?: GovernedExecution | null };
type Explanation = { provider: string; summary: string; rationale: string; safety_note: string };
type Readiness = { version: string; overall_status: string; summary: { agents: number; policies: number; approvals_pending: number; tool_executions: number; audit_events: number; decisions: Record<string, number> }; checks: { name: string; status: string; evidence: string }[] };
type DemoFlow = { duration_minutes: string; steps: { order: number; title: string; goal: string }[]; required_evidence: string[] };

type TabKey = "overview" | "simulate" | "agent" | "approvals" | "audit" | "readiness";

const roleByToken = Object.entries(demoTokens).find(([, token]) => token === getToken())?.[0] as DemoRole | undefined;
const decisionLabels: Record<string, string> = { allow: "Allowed", deny: "Denied", requires_approval: "Needs approval" };

function App() {
  const [role, setRole] = useState<DemoRole>(roleByToken || "admin");
  const [tab, setTab] = useState<TabKey>("overview");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [audits, setAudits] = useState<AuditEvent[]>([]);
  const [readiness, setReadiness] = useState<Readiness | null>(null);
  const [demoFlow, setDemoFlow] = useState<DemoFlow | null>(null);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [agentRun, setAgentRun] = useState<AgentRun | null>(null);
  const [explanation, setExplanation] = useState<Explanation | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [auditResult, setAuditResult] = useState("");
  const [auditType, setAuditType] = useState("");
  const [agentPrompt, setAgentPrompt] = useState("Notify the capstone demo channel that AgentGuard final release is ready for review.");
  const [policySearch, setPolicySearch] = useState("");
  const [simulation, setSimulation] = useState({
    agent_name: "customer-support-agent",
    user_email: "developer@demo.local",
    action: "read",
    resource_name: "customer_profile",
    environment: "sandbox",
    context: '{"customer_id":"C-10045","country":"Kenya"}',
  });

  const canSeeAudit = role === "admin" || role === "auditor";
  const canSeeApprovals = role === "admin" || role === "approver" || role === "auditor";
  const canSeeExecutions = role === "admin" || role === "developer" || role === "approver" || role === "auditor";
  const canSimulate = role === "admin" || role === "developer";

  const auditQuery = useMemo(() => {
    const params = new URLSearchParams();
    if (auditResult) params.set("result", auditResult);
    if (auditType) params.set("event_type", auditType);
    return params.toString() ? `?${params.toString()}` : "";
  }, [auditResult, auditType]);

  const filteredPolicies = useMemo(() => {
    const search = policySearch.trim().toLowerCase();
    if (!search) return policies;
    return policies.filter((policy) => [policy.name, policy.effect, JSON.stringify(policy.conditions)].join(" ").toLowerCase().includes(search));
  }, [policies, policySearch]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const requests: Promise<unknown>[] = [apiGet("/dashboard/metrics"), apiGet("/agents"), apiGet("/policies")];
      if (canSeeApprovals) requests.push(apiGet("/approvals"));
      if (canSeeExecutions) requests.push(apiGet("/executions"));
      if (canSeeAudit) requests.push(apiGet(`/audit-events${auditQuery}`));
      requests.push(apiGet("/release/readiness"));
      requests.push(apiGet("/release/demo-flow"));
      const values = await Promise.all(requests);
      setMetrics(values[0] as Metrics);
      setAgents(values[1] as Agent[]);
      setPolicies(values[2] as Policy[]);
      let index = 3;
      if (canSeeApprovals) setApprovals(values[index++] as Approval[]); else setApprovals([]);
      if (canSeeExecutions) setExecutions(values[index++] as Execution[]); else setExecutions([]);
      if (canSeeAudit) setAudits(values[index++] as AuditEvent[]); else setAudits([]);
      setReadiness(values[index++] as Readiness);
      setDemoFlow(values[index] as DemoFlow);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load AgentGuard data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, [role, auditQuery]);

  function switchRole(nextRole: DemoRole) {
    setDemoRole(nextRole);
    setRole(nextRole);
    setDecision(null);
    setAgentRun(null);
    setExplanation(null);
    setNotice(`Switched to the ${nextRole} role.`);
  }

  async function submitSimulation(event: FormEvent) {
    event.preventDefault();
    try {
      setError("");
      const result = await apiPost("/decisions/evaluate", { ...simulation, context: JSON.parse(simulation.context || "{}") });
      setDecision(result as Decision);
      setExplanation(null);
      setNotice("Action evaluated and recorded in the audit trail.");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Simulation failed");
    }
  }

  async function quickScenario(label: string, resource_name: string, action: string, environment = "sandbox") {
    const next = { ...simulation, resource_name, action, environment };
    setSimulation(next);
    try {
      setError("");
      const result = await apiPost("/decisions/evaluate", { ...next, context: JSON.parse(next.context || "{}") });
      setDecision(result as Decision);
      setNotice(`${label} scenario completed.`);
      await load();
      setTab("simulate");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Scenario failed");
    }
  }

  async function runGovernedAgent(event?: FormEvent) {
    event?.preventDefault();
    try {
      setError("");
      setExplanation(null);
      const result = await apiPost("/agent-runtime/run", {
        agent_name: "customer-support-agent",
        prompt: agentPrompt,
        environment: "sandbox",
        auto_execute: true,
      });
      setAgentRun(result as AgentRun);
      setNotice("The agent proposed a tool call and AgentGuard governed the request before execution.");
      await load();
      setTab("agent");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Governed agent run failed");
    }
  }

  async function explainRequest(actionRequestId: number) {
    try {
      const result = await apiPost("/assistant/explain-decision", { action_request_id: actionRequestId });
      setExplanation(result as Explanation);
      setTab("agent");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Decision explanation failed");
    }
  }

  async function reviewApproval(id: number, action: "approve" | "reject") {
    try {
      await apiPost(`/approvals/${id}/${action}`, { notes: `${action}d during the final AgentGuard demo.` });
      setNotice(`Approval request #${id} was ${action}d.`);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Approval review failed");
    }
  }

  async function exportAudit(format: "csv" | "json") {
    try {
      const separator = auditQuery ? "&" : "?";
      await apiDownload(`/audit-events/export${auditQuery}${separator}format=${format}`, `agentguard-final-audit.${format}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Audit export failed");
    }
  }

  const readinessScore = readiness ? Math.round((readiness.checks.filter((item) => item.status === "complete").length / readiness.checks.length) * 100) : 0;

  return (
    <main>
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow">Quantic MSSE Capstone · Final Release v1.0.0</div>
          <h1>AgentGuard</h1>
          <p>Govern AI agents with deterministic policies, approval gates, controlled tool execution, MCP-ready adapters, AI explanations and audit evidence.</p>
          <div className="hero-actions">
            <button onClick={() => void quickScenario("Allow", "customer_profile", "read")}>Run allow</button>
            <button className="secondary" onClick={() => void quickScenario("Approval", "customer_transactions", "read")}>Run approval</button>
            <button className="ghost" onClick={() => void runGovernedAgent()}>Run agent</button>
          </div>
        </div>
        <div className="command-card">
          <div className="ring" style={{ background: `conic-gradient(#22c55e ${readinessScore * 3.6}deg, rgba(255,255,255,.2) 0deg)` }}><span>{readinessScore}%</span></div>
          <p>Final readiness</p>
          <label>Demo role<select value={role} onChange={(event) => switchRole(event.target.value as DemoRole)}>{Object.keys(demoTokens).map((item) => <option key={item} value={item}>{item}</option>)}</select></label>
        </div>
      </section>

      {error && <section className="banner error"><strong>Action required:</strong> {error}</section>}
      {notice && <section className="banner notice">{notice}</section>}
      {loading && <section className="banner subtle">Refreshing live governance data...</section>}

      <nav className="tabs" aria-label="AgentGuard sections">
        {(["overview", "simulate", "agent", "approvals", "audit", "readiness"] as TabKey[]).map((item) => (
          <button key={item} className={tab === item ? "active" : ""} onClick={() => setTab(item)}>{item}</button>
        ))}
      </nav>

      {tab === "overview" && <Overview metrics={metrics} agents={agents} policies={filteredPolicies} executions={executions} policySearch={policySearch} setPolicySearch={setPolicySearch} />}
      {tab === "simulate" && <Simulation simulation={simulation} setSimulation={setSimulation} submitSimulation={submitSimulation} decision={decision} explainRequest={explainRequest} canSimulate={canSimulate} quickScenario={quickScenario} />}
      {tab === "agent" && <AgentRuntime prompt={agentPrompt} setPrompt={setAgentPrompt} run={runGovernedAgent} agentRun={agentRun} explanation={explanation} explainRequest={explainRequest} />}
      {tab === "approvals" && <ApprovalQueue approvals={approvals} executions={executions} reviewApproval={reviewApproval} canReview={role === "admin" || role === "approver"} />}
      {tab === "audit" && <AuditTrail audits={audits} auditResult={auditResult} auditType={auditType} setAuditResult={setAuditResult} setAuditType={setAuditType} exportAudit={exportAudit} canSeeAudit={canSeeAudit} />}
      {tab === "readiness" && <Readiness readiness={readiness} demoFlow={demoFlow} />}
    </main>
  );
}

function Overview({ metrics, agents, policies, executions, policySearch, setPolicySearch }: { metrics: Metrics | null; agents: Agent[]; policies: Policy[]; executions: Execution[]; policySearch: string; setPolicySearch: (value: string) => void }) {
  return <section className="page-grid">
    <article className="metric-card"><span>Agents</span><strong>{metrics?.agents ?? 0}</strong><small>Registered identities</small></article>
    <article className="metric-card"><span>Active policies</span><strong>{metrics?.active_policies ?? 0}</strong><small>{metrics?.policies ?? 0} total</small></article>
    <article className="metric-card"><span>Approvals</span><strong>{metrics?.pending_approvals ?? 0}</strong><small>Pending review</small></article>
    <article className="metric-card"><span>Executions</span><strong>{metrics?.tool_executions ?? 0}</strong><small>Governed tool calls</small></article>
    <article className="panel wide-panel">
      <div className="section-head"><div><p className="kicker">Decision distribution</p><h2>Governance outcomes</h2></div></div>
      <div className="outcome-row"><Outcome label="Allow" value={metrics?.decisions.allow ?? 0} kind="allow" /><Outcome label="Needs approval" value={metrics?.decisions.requires_approval ?? 0} kind="approval" /><Outcome label="Deny" value={metrics?.decisions.deny ?? 0} kind="deny" /></div>
    </article>
    <article className="panel">
      <div className="section-head"><div><p className="kicker">Registry</p><h2>Agent capabilities</h2></div><span>{agents.length}</span></div>
      <div className="cards">{agents.map((agent) => <div className="list-card" key={agent.id}><div><strong>{agent.name}</strong><p>{agent.purpose}</p></div><span className={`risk ${agent.risk_level}`}>{agent.risk_level}</span></div>)}</div>
    </article>
    <article className="panel">
      <div className="section-head"><div><p className="kicker">Controls</p><h2>Versioned policies</h2></div><input className="search" placeholder="Search policies" value={policySearch} onChange={(event) => setPolicySearch(event.target.value)} /></div>
      <div className="cards policy-list">{policies.map((policy) => <div className="list-card" key={policy.id}><div><span className={`pill ${policy.effect === "requires_approval" ? "approval" : policy.effect}`}>{policy.effect}</span><strong>{policy.name}</strong><p>Priority {policy.priority} · Version {policy.version} · {policy.active ? "active" : "inactive"}</p><code>{JSON.stringify(policy.conditions)}</code></div></div>)}</div>
    </article>
    <article className="panel wide-panel">
      <div className="section-head"><div><p className="kicker">Execution evidence</p><h2>Recent tool execution results</h2></div><span>{executions.length} records</span></div>
      <Table rows={executions.slice(0, 8).map((execution) => [String(execution.id), execution.tool_name, execution.provider, execution.status, String(execution.attempt_count)])} headers={["ID", "Tool", "Provider", "Status", "Attempts"]} />
    </article>
  </section>;
}

function Simulation({ simulation, setSimulation, submitSimulation, decision, explainRequest, canSimulate, quickScenario }: { simulation: typeof initialSimulation; setSimulation: (value: typeof initialSimulation) => void; submitSimulation: (event: FormEvent) => void; decision: Decision | null; explainRequest: (id: number) => Promise<void>; canSimulate: boolean; quickScenario: (label: string, resource: string, action: string, env?: string) => Promise<void> }) {
  return <section className="split-layout"><article className="panel"><div className="section-head"><div><p className="kicker">Policy decision service</p><h2>Action simulator</h2></div><span className="badge">deterministic</span></div>{canSimulate ? <form onSubmit={submitSimulation} className="form-grid"><label>Agent<input value={simulation.agent_name} onChange={(event) => setSimulation({ ...simulation, agent_name: event.target.value })} /></label><label>Environment<select value={simulation.environment} onChange={(event) => setSimulation({ ...simulation, environment: event.target.value })}><option>sandbox</option><option>staging</option><option>production</option></select></label><label>Action<input value={simulation.action} onChange={(event) => setSimulation({ ...simulation, action: event.target.value })} /></label><label>Resource<input value={simulation.resource_name} onChange={(event) => setSimulation({ ...simulation, resource_name: event.target.value })} /></label><label className="wide">Context JSON<textarea rows={5} value={simulation.context} onChange={(event) => setSimulation({ ...simulation, context: event.target.value })} /></label><button type="submit">Evaluate and audit</button></form> : <p>Switch to admin or developer to run simulations.</p>}<div className="quick-actions"><button className="secondary" onClick={() => void quickScenario("Allow", "customer_profile", "read")}>Allow</button><button className="secondary" onClick={() => void quickScenario("Approval", "customer_transactions", "read")}>Approval</button><button className="secondary" onClick={() => void quickScenario("Deny", "customer_profile", "read", "production")}>Deny</button></div></article><article className="panel result-panel"><p className="kicker">Latest decision</p>{decision ? <DecisionCard decision={decision} onExplain={explainRequest} /> : <EmptyState title="No decision yet" text="Run a quick scenario or submit a custom action to generate a correlated decision." />}</article></section>;
}

const initialSimulation = { agent_name: "customer-support-agent", user_email: "developer@demo.local", action: "read", resource_name: "customer_profile", environment: "sandbox", context: '{"customer_id":"C-10045","country":"Kenya"}' };

function AgentRuntime({ prompt, setPrompt, run, agentRun, explanation, explainRequest }: { prompt: string; setPrompt: (value: string) => void; run: (event?: FormEvent) => Promise<void>; agentRun: AgentRun | null; explanation: Explanation | null; explainRequest: (id: number) => Promise<void> }) {
  return <section className="split-layout"><article className="panel"><div className="section-head"><div><p className="kicker">AI agent governance</p><h2>Agent → Policy → Approval → Tool</h2></div><span className="badge">mock-safe MCP</span></div><form onSubmit={(event) => void run(event)} className="form-grid"><label className="wide">Agent instruction<textarea rows={6} value={prompt} onChange={(event) => setPrompt(event.target.value)} /></label><div className="wide quick-actions"><button type="submit">Run governed agent</button><button type="button" className="secondary" onClick={() => setPrompt("Append a case note that the customer requested a follow-up call.")}>Case note</button><button type="button" className="secondary" onClick={() => setPrompt("Read the customer profile for the support case.")}>Profile read</button></div></form></article><article className="panel result-panel"><p className="kicker">Governance trace</p>{agentRun ? <div className="trace"><span className="pill neutral">{agentRun.provider}</span><h2>{agentRun.plan.tool_name}</h2><p>{agentRun.plan.rationale}</p><code>{JSON.stringify(agentRun.plan.arguments)}</code>{agentRun.governance && <><div className="timeline"><span>Decision</span><strong>{agentRun.governance.decision}</strong><span>Execution</span><strong>{agentRun.governance.execution.status}</strong></div><button className="secondary" onClick={() => void explainRequest(agentRun.governance!.action_request_id)}>Explain decision</button></>}{explanation && <div className="explanation"><strong>{explanation.summary}</strong><p>{explanation.rationale}</p><small>{explanation.safety_note}</small></div>}</div> : <EmptyState title="No agent run yet" text="Run a prompt to see the plan, policy decision, execution status and audit correlation ID." />}</article></section>;
}

function ApprovalQueue({ approvals, executions, reviewApproval, canReview }: { approvals: Approval[]; executions: Execution[]; reviewApproval: (id: number, action: "approve" | "reject") => Promise<void>; canReview: boolean }) {
  return <section className="panel"><div className="section-head"><div><p className="kicker">Human-in-the-loop</p><h2>Approval queue</h2></div><span>{approvals.filter((item) => item.status === "pending").length} pending</span></div><Table rows={approvals.map((approval) => [String(approval.id), `#${approval.action_request_id}`, approval.status, approval.reviewer_email || "-", approval.expires_at ? new Date(approval.expires_at).toLocaleString() : "-"])} headers={["ID", "Request", "Status", "Reviewer", "Expires"]} />{canReview && <div className="approval-actions">{approvals.filter((approval) => approval.status === "pending").map((approval) => <div className="approval-card" key={approval.id}><span>Request #{approval.action_request_id}</span><div><button onClick={() => void reviewApproval(approval.id, "approve")}>Approve</button><button className="danger" onClick={() => void reviewApproval(approval.id, "reject")}>Reject</button></div></div>)}</div>}<div className="section-head"><div><p className="kicker">Execution trail</p><h2>Tool executions</h2></div><span>{executions.length}</span></div><Table rows={executions.map((execution) => [String(execution.id), execution.tool_name, execution.status, execution.provider, execution.idempotency_key])} headers={["ID", "Tool", "Status", "Provider", "Idempotency"]} /></section>;
}

function AuditTrail({ audits, auditResult, auditType, setAuditResult, setAuditType, exportAudit, canSeeAudit }: { audits: AuditEvent[]; auditResult: string; auditType: string; setAuditResult: (value: string) => void; setAuditType: (value: string) => void; exportAudit: (format: "csv" | "json") => Promise<void>; canSeeAudit: boolean }) {
  if (!canSeeAudit) return <section className="panel"><EmptyState title="Audit access restricted" text="Switch to admin or auditor to view and export audit evidence." /></section>;
  return <section className="panel"><div className="section-head"><div><p className="kicker">Evidence and audit</p><h2>Searchable audit trail</h2></div><div className="quick-actions"><button className="secondary" onClick={() => void exportAudit("csv")}>Export CSV</button><button className="secondary" onClick={() => void exportAudit("json")}>Export JSON</button></div></div><div className="filters"><label>Result<input value={auditResult} placeholder="success / blocked" onChange={(event) => setAuditResult(event.target.value)} /></label><label>Event type<input value={auditType} placeholder="policy_created" onChange={(event) => setAuditType(event.target.value)} /></label></div><div className="audit-feed">{audits.map((event) => <div key={event.id} className="audit-item"><span className={`dot ${event.result.includes("block") || event.result.includes("deny") ? "deny" : "allow"}`} /><div><strong>{event.event_type}</strong><p>{event.message}</p><small>{event.actor_email} · {event.correlation_id || "no correlation"}</small></div><time>{new Date(event.created_at).toLocaleString()}</time></div>)}</div></section>;
}

function Readiness({ readiness, demoFlow }: { readiness: Readiness | null; demoFlow: DemoFlow | null }) {
  return <section className="split-layout"><article className="panel"><div className="section-head"><div><p className="kicker">Final release readiness</p><h2>Submission checklist</h2></div><span className="badge">{readiness?.overall_status ?? "loading"}</span></div><div className="checklist">{readiness?.checks.map((check) => <div className="check" key={check.name}><span>✓</span><div><strong>{check.name}</strong><p>{check.evidence}</p></div></div>)}</div></article><article className="panel"><div className="section-head"><div><p className="kicker">Presentation plan</p><h2>15-20 minute demo flow</h2></div><span>{demoFlow?.duration_minutes}</span></div><ol className="demo-flow">{demoFlow?.steps.map((step) => <li key={step.order}><strong>{step.title}</strong><p>{step.goal}</p></li>)}</ol></article></section>;
}

function DecisionCard({ decision, onExplain }: { decision: Decision; onExplain: (id: number) => Promise<void> }) {
  return <div className="decision-card"><span className={`pill ${decision.decision === "requires_approval" ? "approval" : decision.decision}`}>{decisionLabels[decision.decision] || decision.decision}</span><h2>{decision.reason}</h2><dl><div><dt>Correlation</dt><dd>{decision.correlation_id}</dd></div><div><dt>Matched policy</dt><dd>{decision.matched_policy_name || "Default"}</dd></div><div><dt>Policies evaluated</dt><dd>{decision.evaluated_policy_count}</dd></div></dl>{decision.action_request_id && <button className="secondary" onClick={() => void onExplain(decision.action_request_id!)}>Explain with AI</button>}</div>;
}

function Metric({ label, value }: { label: string; value: number }) { return <article className="metric-card"><span>{label}</span><strong>{value}</strong></article>; }
function Outcome({ label, value, kind }: { label: string; value: number; kind: string }) { return <div className={`outcome ${kind}`}><strong>{value}</strong><span>{label}</span></div>; }
function EmptyState({ title, text }: { title: string; text: string }) { return <div className="empty"><strong>{title}</strong><p>{text}</p></div>; }
function Table({ headers, rows }: { headers: string[]; rows: string[][] }) { return <div className="table-wrap"><table><thead><tr>{headers.map((header) => <th key={header}>{header}</th>)}</tr></thead><tbody>{rows.length ? rows.map((row, index) => <tr key={index}>{row.map((cell, cellIndex) => <td key={cellIndex}>{cell}</td>)}</tr>) : <tr><td colSpan={headers.length}>No records yet.</td></tr>}</tbody></table></div>; }

createRoot(document.getElementById("root")!).render(<App />);
