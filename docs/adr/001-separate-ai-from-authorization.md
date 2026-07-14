# ADR-001: Separate AI Explanations from Authorization Decisions

## Status
Accepted

## Context
AI-generated responses can be non-deterministic and difficult to audit. The platform needs predictable governance behavior.

## Decision
Authorization is decided only by the deterministic policy engine. The AI assistant may explain a completed decision but cannot change it.

## Consequences
- Decisions are testable and reproducible.
- Explanations are safer and easier to validate.
- The platform still demonstrates AI engineering without relying on AI for critical access control.
