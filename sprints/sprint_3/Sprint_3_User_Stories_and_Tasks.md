# Sprint 3 User Stories and Tasks

Sprint goal: complete human approvals, governed tool execution, real-agent adapter support, MCP integration, grounded AI explanations, security guardrails, UI workflows, and end-to-end evidence.

## Epic 300: AG Sprint 3 — Human Approval, Real Agent/MCP, and AI Explanations

Deliver a governed end-to-end workflow in which real agent tool requests are allowed, denied, or held for human approval and fully audited.

### Story 310: Complete the human approval lifecycle

**Story points:** 8  
**Priority:** Highest  
**Acceptance criteria:** Authorized approvers can approve or reject pending requests, self-approval and invalid transitions are blocked, and every transition is audited.

Provide a secure approval queue and deterministic state transitions for sensitive agent actions.

- **Task 311 - Implement approval queue and detail APIs**: Add organization-scoped list, filter, and detail endpoints for pending and completed approvals.
- **Task 312 - Implement approve, reject, expire, and cancel transitions**: Enforce valid state transitions and persist reviewer, reason, timestamps, and final outcome.
- **Task 313 - Prevent self-approval and duplicate processing**: Block requesters from approving their own actions and make approval operations idempotent.
### Story 320: Execute governed tools safely

**Story points:** 8  
**Priority:** Highest  
**Acceptance criteria:** Denied requests never execute, approval-required requests execute only after approval, and successful or failed executions are recorded exactly once.

Create a tool-execution layer that runs an external action only after AgentGuard authorizes it.

- **Task 321 - Create provider-neutral tool adapter interface**: Define a common adapter contract for tool discovery, argument validation, execution, and normalized results.
- **Task 322 - Add idempotent execution records**: Store execution status, attempt count, timestamps, provider response, and idempotency key.
- **Task 323 - Handle tool timeout, failure, and retry safely**: Add bounded timeouts, safe retry rules, failure auditing, and user-visible error states.
### Story 330: Integrate a real AI agent

**Story points:** 8  
**Priority:** Highest  
**Acceptance criteria:** The agent can submit structured tool requests, cannot bypass AgentGuard, and its request, decision, and result share one correlation ID.

Connect one real AI agent that proposes tool calls through the AgentGuard governance gateway.

- **Task 331 - Implement agent adapter and structured request schema**: Translate agent tool-call proposals into the common AgentGuard action-request model.
- **Task 332 - Register agent identity and permitted capabilities**: Bind the agent to its registered identity, owner, permitted tools, and environment.
- **Task 333 - Add mock mode for deterministic local and CI testing**: Provide a provider-free mock agent so tests and demonstrations do not depend on external availability.
### Story 340: Integrate one MCP tool provider

**Story points:** 8  
**Priority:** Highest  
**Acceptance criteria:** AgentGuard discovers only approved tools, validates arguments, governs each invocation, and successfully demonstrates at least two non-destructive test actions.

Connect AgentGuard to one MCP server, such as a safely configured Zapier MCP endpoint, using a small allowlisted tool set.

- **Task 341 - Configure MCP client and secret handling**: Load the MCP endpoint and credentials from environment variables and document secure setup.
- **Task 342 - Allowlist safe MCP tools and argument schemas**: Expose only selected non-destructive tools and validate destination, channel, sheet, or project constraints.
- **Task 343 - Implement MCP mock server or stub**: Provide deterministic local and CI behavior when the real MCP service is unavailable.
### Story 350: Explain policy decisions with AI without changing them

**Story points:** 5  
**Priority:** High  
**Acceptance criteria:** Explanations reference the matched policy and request context, follow a validated schema, and can never alter the authorization decision.

Generate grounded plain-language explanations from the immutable deterministic decision record.

- **Task 351 - Create model-provider abstraction and mock provider**: Support a configurable AI provider and a deterministic local fallback.
- **Task 352 - Build grounded explanation prompt and output schema**: Provide only approved decision data and validate the returned summary, rationale, and caution fields.
- **Task 353 - Handle AI provider failure safely**: Return the original deterministic decision and a safe fallback explanation when the provider fails.
### Story 360: Add agent and MCP security guardrails

**Story points:** 8  
**Priority:** Highest  
**Acceptance criteria:** Malicious prompts and tool arguments are rejected or escalated, secrets are redacted, and tests prove that no execution bypasses policy evaluation.

Protect the governance path from prompt injection, unsafe arguments, secret leakage, and direct tool bypass.

- **Task 361 - Validate and sanitize tool arguments**: Reject unexpected fields, unsafe destinations, destructive actions, and oversized payloads.
- **Task 362 - Add prompt-injection and bypass test cases**: Create an evaluation set covering instruction override, hidden actions, direct execution, and policy-evasion attempts.
- **Task 363 - Redact secrets and sensitive fields from logs and prompts**: Define redaction rules and verify that credentials and sensitive values are not exposed.
### Story 370: Provide an end-to-end governance interface

**Story points:** 8  
**Priority:** High  
**Acceptance criteria:** A reviewer can complete the full request-to-decision-to-approval-to-execution workflow from the web interface.

Expose pending approvals, execution status, agent requests, policy decisions, and AI explanations in the React application.

- **Task 371 - Build approval queue and review screens**: Add filters, request context, matched policy, approve/reject forms, and reviewer notes.
- **Task 372 - Display execution timeline and correlation data**: Show request, decision, approval, execution, result, and audit events as one trace.
- **Task 373 - Display grounded AI explanations and failure states**: Present explanations separately from the authoritative decision and handle provider errors clearly.
### Story 380: Test, document, and demonstrate Sprint 3

**Story points:** 5  
**Priority:** Highest  
**Acceptance criteria:** Backend, frontend, approval, MCP, security, and end-to-end tests pass and the Sprint 3 demonstration shows allow, deny, approval, execution, and audit scenarios.

Provide repeatable test evidence, release documentation, Jira evidence, and a sprint review recording for the real governed-agent workflow.

- **Task 381 - Add approval, agent, MCP, and end-to-end tests**: Cover state transitions, idempotency, provider failure, bypass prevention, and governed execution.
- **Task 382 - Update architecture, threat model, and AI evaluation docs**: Document adapters, trust boundaries, failure behavior, model limitations, and security controls.
- **Task 383 - Create Sprint 3 release notes and demo evidence**: Record completed stories, limitations, test results, screenshots, Jira links, and sprint review video.
