# Agent Collaboration Frameworks

Patterns and implementations for multi-agent collaboration — role-based teams, conversation-driven workflows, and orchestration patterns inspired by AutoGen, CrewAI, and LangGraph.

## Overview

Modern AI agent systems achieve complex tasks by having multiple specialized agents work together. This repository implements the key collaboration patterns from scratch so you can understand how frameworks like CrewAI and AutoGen work under the hood.

```
    ┌───────────────────────────────────────────────────┐
    │              Orchestrator / Manager                │
    │   Assigns tasks, monitors progress, aggregates    │
    └─────┬─────────────┬──────────────┬───────────────┘
          │             │              │
    ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
    │ Researcher│ │  Writer   │ │ Reviewer  │
    │   Agent   │ │   Agent   │ │   Agent   │
    │           │ │           │ │           │
    │ search()  │ │ draft()   │ │ review()  │
    │ analyze() │ │ edit()    │ │ score()   │
    └───────────┘ └───────────┘ └───────────┘
```

## Key Patterns

| Pattern | Description |
|---------|-------------|
| **Role-Based Team** | Each agent has a specialized role (researcher, writer, reviewer) |
| **Sequential Pipeline** | Output of one agent feeds into the next |
| **Conversation Loop** | Agents discuss and refine through multi-turn dialogue |
| **Supervisor Pattern** | A manager agent delegates and reviews work |
| **Peer Review** | Agents evaluate each other's outputs |
| **Tool-Augmented** | Agents use tools (search, code execution) to accomplish tasks |

## Examples

| File | Description |
|------|-------------|
| `01_role_based_team.py` | CrewAI-style team with researcher, writer, and reviewer agents |
| `02_conversation_loop.py` | AutoGen-style multi-turn conversation between agents |
| `03_pipeline_orchestrator.py` | Sequential pipeline with supervisor oversight |

## Best Practices

1. **Define clear agent roles** — each agent should have a specific responsibility
2. **Use structured message formats** — standard message schema enables interoperability
3. **Implement quality gates** — reviewer agents prevent poor output from propagating
4. **Add timeout and retry logic** — agents can get stuck in loops
5. **Make collaboration observable** — log all agent-to-agent messages for debugging
6. **Start with sequential, evolve to parallel** — get the pipeline working before optimizing

## References

- [microsoft/autogen](https://github.com/microsoft/autogen) — Multi-agent conversation framework
- [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) — Role-based agent orchestration
- [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) — Graph-based agent workflows
- [camel-ai/camel](https://github.com/camel-ai/camel) — Communicative agent framework
- [fetchai/uAgents](https://github.com/fetchai/uAgents) — Lightweight agent framework

## License

MIT
