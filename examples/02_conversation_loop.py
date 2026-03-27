"""
Example 2: Conversation Loop (AutoGen-style)
================================================
Multiple agents discuss a problem through multi-turn conversation,
building on each other's responses until they reach consensus.

Run: python examples/02_conversation_loop.py
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ChatMessage:
    role: str  # agent name
    content: str
    turn: int


class ConversableAgent:
    """An agent that participates in multi-turn conversations."""

    def __init__(self, name: str, system_prompt: str, expertise: dict):
        self.name = name
        self.system_prompt = system_prompt
        self.expertise = expertise  # topic -> list of talking points
        self.conversation_memory = []

    def generate_response(self, chat_history: list, topic: str) -> str:
        """Generate a response based on conversation history and expertise."""
        turn = len([m for m in chat_history if m.role == self.name])

        # Find relevant expertise
        relevant = []
        for key, points in self.expertise.items():
            if any(word in topic.lower() for word in key.lower().split()):
                relevant.extend(points)

        # Generate response based on conversation state
        if turn == 0:
            # First response: share initial perspective
            if relevant:
                point = relevant[0] if relevant else "I don't have specific knowledge on this."
                return f"From my perspective as {self.name}: {point}"
            return f"As {self.name}, I'd like to hear more about the specific requirements."

        # Subsequent turns: build on previous messages
        last_msg = chat_history[-1].content if chat_history else ""

        if turn < len(relevant):
            response = f"Building on that — {relevant[min(turn, len(relevant)-1)]}"
        elif "agree" in last_msg.lower() or "consensus" in last_msg.lower():
            response = f"I agree. Let me add: {relevant[-1] if relevant else 'we should finalize our approach.'}"
        elif "disagree" in last_msg.lower() or "however" in last_msg.lower():
            response = f"I see your point. Let me offer an alternative: {relevant[turn % len(relevant)] if relevant else 'we should reconsider.'}"
        else:
            response = f"Good point. I'd also note: {relevant[turn % len(relevant)] if relevant else 'this needs more analysis.'}"

        return response

    def should_terminate(self, chat_history: list, max_turns: int) -> bool:
        """Decide if conversation should end."""
        my_turns = sum(1 for m in chat_history if m.role == self.name)
        return my_turns >= max_turns


class GroupChat:
    """Manages multi-agent conversations."""

    def __init__(self, agents: list, max_rounds: int = 5):
        self.agents = {a.name: a for a in agents}
        self.max_rounds = max_rounds
        self.history = []

    def _select_next_speaker(self, current: str) -> str:
        """Round-robin speaker selection."""
        names = list(self.agents.keys())
        idx = names.index(current) if current in names else -1
        return names[(idx + 1) % len(names)]

    def run(self, topic: str, initiator: str) -> list:
        """Run the group discussion."""
        print(f"\n  {'─' * 55}")
        print(f"  GROUP CHAT: {topic}")
        print(f"  Participants: {', '.join(self.agents.keys())}")
        print(f"  {'─' * 55}")

        current_speaker = initiator

        for round_num in range(self.max_rounds * len(self.agents)):
            agent = self.agents[current_speaker]

            # Check termination
            if agent.should_terminate(self.history, self.max_rounds):
                current_speaker = self._select_next_speaker(current_speaker)
                continue

            # Generate response
            response = agent.generate_response(self.history, topic)
            msg = ChatMessage(role=current_speaker, content=response, turn=round_num)
            self.history.append(msg)

            print(f"\n  [{current_speaker}] (turn {round_num + 1}):")
            print(f"    {response}")

            # Check if all agents have had enough turns
            all_done = all(
                a.should_terminate(self.history, self.max_rounds)
                for a in self.agents.values()
            )
            if all_done:
                break

            current_speaker = self._select_next_speaker(current_speaker)

        # Synthesize conclusion
        print(f"\n  {'─' * 55}")
        print(f"  CONVERSATION SUMMARY")
        print(f"  {'─' * 55}")
        print(f"  Total messages: {len(self.history)}")
        for name in self.agents:
            count = sum(1 for m in self.history if m.role == name)
            print(f"  {name}: {count} messages")

        return self.history


def create_design_team():
    """Create a team that discusses software architecture decisions."""
    architect = ConversableAgent(
        "Architect",
        "You are a software architect focused on system design",
        {
            "architecture agent system": [
                "We should use a microservices architecture for the agent system — each agent as an independent service",
                "Message queues (like RabbitMQ or Redis Streams) are ideal for agent-to-agent communication",
                "The orchestrator should be stateless and use event sourcing for reliability",
                "We need circuit breakers between agents to handle failures gracefully",
            ],
            "scalability": [
                "Horizontal scaling of agent instances behind a load balancer is essential",
                "State should be externalized to Redis or a database, not held in memory",
            ],
        }
    )

    developer = ConversableAgent(
        "Developer",
        "You are a senior developer focused on implementation",
        {
            "architecture agent system": [
                "Python with asyncio would be ideal — most agent frameworks are Python-based",
                "We should use pydantic for message schemas to ensure type safety between agents",
                "Docker containers for each agent type will simplify deployment and testing",
                "We need comprehensive logging — agent systems are notoriously hard to debug",
            ],
            "implementation": [
                "I suggest starting with a simple synchronous pipeline before adding async",
                "Unit tests for each agent in isolation, integration tests for the full pipeline",
            ],
        }
    )

    security = ConversableAgent(
        "SecurityExpert",
        "You are a security specialist for distributed systems",
        {
            "architecture agent system": [
                "Every agent-to-agent message must be authenticated — we can't trust untrusted agents",
                "Rate limiting on agent actions prevents runaway behavior and resource exhaustion",
                "Sandboxing agents that execute code is non-negotiable — use containers with resource limits",
                "Audit logging of all agent decisions for compliance and debugging",
            ],
            "security": [
                "Input validation at every agent boundary prevents injection attacks",
                "Principle of least privilege — each agent should only access what it needs",
            ],
        }
    )

    return [architect, developer, security]


if __name__ == "__main__":
    print("=== Multi-Agent Conversation Loop ===")

    agents = create_design_team()
    chat = GroupChat(agents, max_rounds=3)

    chat.run(
        topic="Design an agent system architecture for a code review automation tool",
        initiator="Architect"
    )
