# Final Demo Script

Target duration: 15-20 minutes.

| Time | Segment |
|---|---|
| 0:00-1:30 | Introduce AgentGuard and the AI agent governance problem |
| 1:30-3:00 | Explain users, roles, and business value |
| 3:00-4:30 | Show architecture, repository, and CI/CD |
| 4:30-6:30 | Demonstrate dashboard and registry |
| 6:30-9:00 | Demonstrate allow, deny, and approval-required policy decisions |
| 9:00-11:00 | Demonstrate approval workflow |
| 11:00-12:30 | Demonstrate audit logs |
| 12:30-14:00 | Demonstrate AI explanation endpoint |
| 14:00-16:00 | Explain testing, security, and design decisions |
| 16:00-18:00 | Summarize limitations and future work |

## Demo Data

Use these three scenarios:

1. Customer-support agent reads `customer_profile` in sandbox -> allow.
2. Customer-support agent reads `customer_transactions` -> requires approval.
3. Customer-support agent reads `customer_profile` in production -> deny.
