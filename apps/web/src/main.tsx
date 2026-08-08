import React, { FormEvent, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import { apiDownload, apiGet, apiPatch, apiPost, DemoRole, demoTokens, getToken, setDemoRole } from "./api";
import "./styles.css";

type Metrics = {
  agents: number;
  policies: number;
  active_policies: number;
  audit_events: number;
  pending_approvals: number;
  decisions: { allow: number; deny: number; requires_approval: number };
};

type Agent = { id: number; name: string; purpose: string; risk_level: string; status: string };
type Policy = {
  id: number;
  name: string;
  description: string;
  effect: "allow" | "deny" | "requires_approval";
  priority: number;
  active: boolean;
  version: number;
  conditions: Record<string, unknown>;
};
type Approval = { id: number; action_request_id: number; status: string; reviewer_email?: string | null };
type AuditEvent = {
  id: number;
  correlation_id?: string | null;
  actor_email: string;
  event_type: string;
  result: string;
  message: string;
  created_at: string;
};
type Decision = {
  correlation_id: string;
  decision: string;
  reason: string;
  matched_policy_id?: number;
  matched_policy_name?: string;
  evaluated_policy_count: number;
  action_request_id?: number;
  approval_id?: number;
};

const roleByToken = Object.entries(demoTokens).find(([, token]) => token === getToken())?.[0] as DemoRole | undefined;

function App() {
  const [role, setRole] = useState<DemoRole>(roleByToken || "admin");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [policies, setPolicies] = useState<Policy[]>([]);
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [audits, setAudits] = useState<AuditEvent[]>([]);
  const [decision, setDecision] = useState<Decision | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [auditResult, setAuditResult] = useState("");
  const [auditType, setAuditType] = useState("");

  const [simulation, setSimulation] = useState({
    agent_name: "customer-support-agent",
    user_email: "developer@demo.local",
    action: "read",
    resource_name: "customer_profile",
    environment: "sandbox",
    context: '{"customer_id":"C-10045","country":"Kenya"}',
  });

  const [policyDraft, setPolicyDraft] = useState({
    name: "",
    description: "",
    effect: "allow",
    priority: "100",
    conditions: '{"agent_name":"customer-support-agent","resource_name":"customer_profile","action":"read","environment":"sandbox"}',
  });

  const canSeeAudit = role === "admin" || role === "auditor";
  const canSeeApprovals = role === "admin" || role === "approver" || role === "auditor";
  const canManagePolicies = role === "admin";
  const canSimulate = role === "admin" || role === "developer";

  const auditQuery = useMemo(() => {
    const params = new URLSearchParams();
    if (auditResult) params.set("result", auditResult);
    if (auditType) params.set("event_type", auditType);
    return params.toString() ? `?${params.toString()}` : "";
  }, [auditResult, auditType]);

  async function load() {
    setLoading(true);
    setError("");
    try {
      const requests: Promise<unknown>[] = [apiGet("/dashboard/metrics"), apiGet("/agents"), apiGet("/policies")];
      if (canSeeApprovals) requests.push(apiGet("/approvals"));
      if (canSeeAudit) requests.push(apiGet(`/audit-events${auditQuery}`));
      const values = await Promise.all(requests);
      setMetrics(values[0] as Metrics);
      setAgents(values[1] as Agent[]);
      setPolicies(values[2] as Policy[]);
      let index = 3;
      if (canSeeApprovals) setApprovals(values[index++] as Approval[]);
      else setApprovals([]);
      if (canSeeAudit) setAudits(values[index] as AuditEvent[]);
      else setAudits([]);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load AgentGuard data");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, [role, auditQuery]);

  function switchRole(nextRole: DemoRole) {
    setDemoRole(nextRole);
    setRole(nextRole);
    setDecision(null);
    setNotice(`Switched to the ${nextRole} demonstration role.`);
  }

  async function submitSimulation(event: FormEvent) {
    event.preventDefault();
    setError("");
    setNotice("");
    try {
      const result = await apiPost("/decisions/evaluate", {
        ...simulation,
        context: JSON.parse(simulation.context || "{}"),
      });
      setDecision(result as Decision);
      setNotice("The action was evaluated and an audit event was created.");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Simulation failed");
    }
  }

  async function runScenario(resource_name: string, action: string, environment = "sandbox") {
    const next = { ...simulation, resource_name, action, environment };
    setSimulation(next);
    try {
      const result = await apiPost("/decisions/evaluate", {
        ...next,
        context: JSON.parse(next.context || "{}"),
      });
      setDecision(result as Decision);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Scenario failed");
    }
  }

  async function createPolicy(event: FormEvent) {
    event.preventDefault();
    try {
      await apiPost("/policies", {
        name: policyDraft.name,
        description: policyDraft.description,
        effect: policyDraft.effect,
        priority: Number(policyDraft.priority),
        conditions: JSON.parse(policyDraft.conditions),
      });
      setPolicyDraft({ ...policyDraft, name: "", description: "" });
      setNotice("Policy created with version 1 and recorded in the audit trail.");
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Policy creation failed");
    }
  }

  async function togglePolicy(policy: Policy) {
    try {
      await apiPost(`/policies/${policy.id}/${policy.active ? "deactivate" : "activate"}`, {});
      setNotice(`Policy ${policy.active ? "deactivated" : "activated"}.`);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Policy update failed");
    }
  }

  async function reviewApproval(id: number, action: "approve" | "reject") {
    try {
      await apiPost(`/approvals/${id}/${action}`, { notes: `${action}d during the AgentGuard demonstration.` });
      setNotice(`Approval request ${id} was ${action}d.`);
      await load();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Approval review failed");
    }
  }

  async function exportAudit(format: "csv" | "json") {
    try {
      const separator = auditQuery ? "&" : "?";
      await apiDownload(`/audit-events/export${auditQuery}${separator}format=${format}`, `agentguard-audit.${format}`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Audit export failed");
    }
  }

  return (
    <main>
      <header className="hero">
        <div>
          <p className="eyebrow">Quantic MSSE Capstone · Sprint 2</p>
          <h1>AgentGuard</h1>
          <p className="heroCopy">Govern AI-agent actions with deterministic policies, contextual evaluation, human review, and an exportable audit trail.</p>
        </div>
        <label className="rolePicker">
          Demonstration role
          <select value={role} onChange={(event) => switchRole(event.target.value as DemoRole)}>
            {Object.keys(demoTokens).map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
        </label>
      </header>

      {error && <section className="banner error"><strong>Action required:</strong> {error}</section>}
      {notice && <section className="banner notice">{notice}</section>}
      {loading && <p className="loading">Refreshing governance data…</p>}

      <section className="metrics">
        <Metric label="Registered agents" value={metrics?.agents ?? 0} />
        <Metric label="Active policies" value={metrics?.active_policies ?? 0} />
        <Metric label="Pending approvals" value={metrics?.pending_approvals ?? 0} />
        <Metric label="Audit events" value={metrics?.audit_events ?? 0} />
      </section>

      {metrics && (
        <section className="decisionSummary">
          <span className="pill allow">Allow: {metrics.decisions.allow}</span>
          <span className="pill approval">Approval: {metrics.decisions.requires_approval}</span>
          <span className="pill deny">Deny: {metrics.decisions.deny}</span>
        </section>
      )}

      <section className="grid twoColumns">
        <article className="panel">
          <div className="sectionHeading">
            <div><p className="kicker">Policy decision service</p><h2>Action simulator</h2></div>
            <span className="versionTag">API v0.2.0</span>
          </div>
          {canSimulate ? (
            <form onSubmit={submitSimulation} className="formGrid">
              <label>Agent<select value={simulation.agent_name} onChange={(event) => setSimulation({ ...simulation, agent_name: event.target.value })}>{agents.map((agent) => <option key={agent.id}>{agent.name}</option>)}</select></label>
              <label>Environment<select value={simulation.environment} onChange={(event) => setSimulation({ ...simulation, environment: event.target.value })}><option>sandbox</option><option>staging</option><option>production</option></select></label>
              <label>Action<input value={simulation.action} onChange={(event) => setSimulation({ ...simulation, action: event.target.value })} /></label>
              <label>Protected resource<input value={simulation.resource_name} onChange={(event) => setSimulation({ ...simulation, resource_name: event.target.value })} /></label>
              <label className="wide">Context JSON<textarea rows={3} value={simulation.context} onChange={(event) => setSimulation({ ...simulation, context: event.target.value })} /></label>
              <div className="wide buttonRow"><button type="submit">Evaluate and audit</button></div>
            </form>
          ) : <p>Your current role can review outcomes but cannot initiate action simulations.</p>}
          <div className="scenarioButtons">
            <button className="secondary" disabled={!canSimulate} onClick={() => void runScenario("customer_profile", "read")}>Allowed profile read</button>
            <button className="secondary" disabled={!canSimulate} onClick={() => void runScenario("customer_transactions", "read")}>Sensitive transaction read</button>
            <button className="secondary" disabled={!canSimulate} onClick={() => void runScenario("customer_profile", "read", "production")}>Denied production access</button>
          </div>
          {decision && <DecisionCard decision={decision} />}
        </article>

        <article className="panel">
          <p className="kicker">Registered capabilities</p>
          <h2>AI agents</h2>
          <div className="cardsList">
            {agents.map((agent) => (
              <div className="listCard" key={agent.id}>
                <div><strong>{agent.name}</strong><p>{agent.purpose}</p></div>
                <span className={`risk ${agent.risk_level}`}>{agent.risk_level}</span>
              </div>
            ))}
          </div>
        </article>
      </section>

      <section className="grid twoColumns">
        <article className="panel">
          <div className="sectionHeading"><div><p className="kicker">Versioned controls</p><h2>Policies</h2></div><span>{policies.length} total</span></div>
          <div className="cardsList policyList">
            {policies.map((policy) => (
              <div className="listCard" key={policy.id}>
                <div>
                  <div className="titleLine"><span className={`pill ${policy.effect === "requires_approval" ? "approval" : policy.effect}`}>{policy.effect}</span><strong>{policy.name}</strong></div>
                  <p>Priority {policy.priority} · Version {policy.version} · {policy.active ? "Active" : "Inactive"}</p>
                  <code>{JSON.stringify(policy.conditions)}</code>
                </div>
                {canManagePolicies && <button className="textButton" onClick={() => void togglePolicy(policy)}>{policy.active ? "Deactivate" : "Activate"}</button>}
              </div>
            ))}
          </div>
        </article>

        <article className="panel">
          <p className="kicker">Administrator workflow</p>
          <h2>Create a policy</h2>
          {canManagePolicies ? (
            <form onSubmit={createPolicy} className="formGrid">
              <label className="wide">Name<input required value={policyDraft.name} onChange={(event) => setPolicyDraft({ ...policyDraft, name: event.target.value })} /></label>
              <label>Effect<select value={policyDraft.effect} onChange={(event) => setPolicyDraft({ ...policyDraft, effect: event.target.value })}><option value="allow">allow</option><option value="requires_approval">requires approval</option><option value="deny">deny</option></select></label>
              <label>Priority<input type="number" min="0" max="10000" value={policyDraft.priority} onChange={(event) => setPolicyDraft({ ...policyDraft, priority: event.target.value })} /></label>
              <label className="wide">Description<textarea rows={2} value={policyDraft.description} onChange={(event) => setPolicyDraft({ ...policyDraft, description: event.target.value })} /></label>
              <label className="wide">Conditions JSON<textarea rows={5} value={policyDraft.conditions} onChange={(event) => setPolicyDraft({ ...policyDraft, conditions: event.target.value })} /></label>
              <div className="wide"><button type="submit">Create versioned policy</button></div>
            </form>
          ) : <p>Switch to the administrator role to create or activate policies.</p>}
        </article>
      </section>

      {canSeeApprovals && (
        <section className="panel">
          <div className="sectionHeading"><div><p className="kicker">Human-in-the-loop preview</p><h2>Approval queue</h2></div><span>{approvals.filter((item) => item.status === "pending").length} pending</span></div>
          <div className="tableWrap"><table><thead><tr><th>ID</th><th>Action request</th><th>Status</th><th>Reviewer</th><th>Actions</th></tr></thead><tbody>{approvals.map((approval) => <tr key={approval.id}><td>#{approval.id}</td><td>#{approval.action_request_id}</td><td><span className={`pill ${approval.status === "pending" ? "approval" : approval.status === "approved" ? "allow" : "deny"}`}>{approval.status}</span></td><td>{approval.reviewer_email || "—"}</td><td>{approval.status === "pending" && (role === "admin" || role === "approver") ? <div className="buttonRow"><button onClick={() => void reviewApproval(approval.id, "approve")}>Approve</button><button className="dangerButton" onClick={() => void reviewApproval(approval.id, "reject")}>Reject</button></div> : "—"}</td></tr>)}</tbody></table></div>
        </section>
      )}

      {canSeeAudit && (
        <section className="panel">
          <div className="sectionHeading"><div><p className="kicker">Searchable evidence</p><h2>Audit trail</h2></div><div className="buttonRow"><button className="secondary" onClick={() => void exportAudit("csv")}>Export CSV</button><button className="secondary" onClick={() => void exportAudit("json")}>Export JSON</button></div></div>
          <div className="filterRow"><label>Result<select value={auditResult} onChange={(event) => setAuditResult(event.target.value)}><option value="">All</option><option>allow</option><option>deny</option><option>requires_approval</option><option>success</option><option>approved</option><option>rejected</option></select></label><label>Event type<select value={auditType} onChange={(event) => setAuditType(event.target.value)}><option value="">All</option><option>policy_decision</option><option>policy_created</option><option>policy_updated</option><option>policy_status_changed</option><option>approval_review</option></select></label></div>
          <div className="auditList">{audits.map((audit) => <div key={audit.id}><div><div className="titleLine"><span className={`pill ${audit.result === "requires_approval" ? "approval" : audit.result === "allow" || audit.result === "success" || audit.result === "approved" ? "allow" : "deny"}`}>{audit.result}</span><strong>{audit.event_type}</strong></div><p>{audit.message}</p><small>{audit.actor_email} · {audit.correlation_id || "no correlation ID"}</small></div><time>{new Date(audit.created_at).toLocaleString()}</time></div>)}</div>
        </section>
      )}
    </main>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return <article><strong>{value}</strong><span>{label}</span></article>;
}

function DecisionCard({ decision }: { decision: Decision }) {
  const className = decision.decision === "requires_approval" ? "approval" : decision.decision;
  return <div className="decisionCard"><div className="titleLine"><span className={`pill ${className}`}>{decision.decision}</span><strong>{decision.matched_policy_name || "Default-deny rule"}</strong></div><p>{decision.reason}</p><dl><div><dt>Correlation ID</dt><dd>{decision.correlation_id}</dd></div><div><dt>Policies evaluated</dt><dd>{decision.evaluated_policy_count}</dd></div><div><dt>Request ID</dt><dd>{decision.action_request_id || "Dry run"}</dd></div></dl></div>;
}

createRoot(document.getElementById("root")!).render(<React.StrictMode><App /></React.StrictMode>);
