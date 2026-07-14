package agentguard

default allow := false

default requires_approval := false

allow if {
  input.agent_name == "customer-support-agent"
  input.resource_name == "customer_profile"
  input.action == "read"
  input.environment == "sandbox"
}

requires_approval if {
  input.resource_name == "customer_transactions"
  input.action == "read"
}
