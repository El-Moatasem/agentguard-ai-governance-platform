# ADR-002: Use Default-Deny Policy Behavior

## Status
Accepted

## Decision
If no active policy matches an agent action request, the system denies the request.

## Consequences
- Reduces accidental over-permission.
- Requires explicit policies for allowed behavior.
- Makes tests and demonstrations clear.
