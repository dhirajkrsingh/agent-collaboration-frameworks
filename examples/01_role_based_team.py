"""
Example 1: Role-Based Agent Team
====================================
A CrewAI-inspired team with specialized agents (researcher, writer, reviewer)
working together to produce a report on a given topic.

Run: python examples/01_role_based_team.py
"""

import random
from dataclasses import dataclass, field


@dataclass
class AgentRole:
    name: str
    description: str
    skills: list


@dataclass
class Task:
    description: str
    assigned_to: str = ""
    status: str = "pending"
    input_data: str = ""
    output_data: str = ""


@dataclass
class Message:
    sender: str
    receiver: str
    content: str
    msg_type: str = "task_result"  # task_result, feedback, request


class BaseAgent:
    """Base class for all team agents."""

    def __init__(self, role: AgentRole):
        self.role = role
        self.inbox = []
        self.work_log = []

    def receive(self, message: Message):
        self.inbox.append(message)

    def process(self, task: Task) -> str:
        raise NotImplementedError


class ResearcherAgent(BaseAgent):
    """Gathers and synthesizes information on a topic."""

    def __init__(self):
        super().__init__(AgentRole(
            "Researcher",
            "Finds and synthesizes information from multiple sources",
            ["search", "analyze", "summarize"]
        ))
        self.knowledge_base = {
            "multi-agent systems": [
                "Multi-agent systems consist of multiple interacting intelligent agents",
                "Key challenges include coordination, communication, and emergent behavior",
                "Applications include robotics, trading, and traffic management",
                "FIPA standards define agent communication language (ACL)",
                "Game theory provides theoretical foundations for agent interactions",
            ],
            "reinforcement learning": [
                "RL agents learn by trial and error through rewards and penalties",
                "Q-learning and policy gradient are fundamental algorithms",
                "Multi-agent RL introduces non-stationarity challenges",
                "Experience replay and target networks stabilize training",
            ],
            "autonomous agents": [
                "Autonomous agents operate without continuous human intervention",
                "They perceive, reason, plan, and act in a continuous loop",
                "Self-correction and monitoring are essential for reliability",
                "Modern examples include AutoGPT, BabyAGI, and Devin",
            ],
        }

    def process(self, task: Task) -> str:
        topic = task.input_data.lower()
        findings = []
        for key, facts in self.knowledge_base.items():
            if any(word in topic for word in key.split()):
                findings.extend(random.sample(facts, min(3, len(facts))))

        if not findings:
            findings = ["No specific data found — using general agent knowledge",
                        "Agents are systems that perceive and act in an environment",
                        "Collaboration between agents enables complex task completion"]

        result = f"Research on '{task.input_data}':\n"
        for i, finding in enumerate(findings, 1):
            result += f"  {i}. {finding}\n"
        result += f"  Sources consulted: {random.randint(3, 8)} papers and repositories"

        self.work_log.append(f"Researched: {task.input_data}")
        task.output_data = result
        task.status = "completed"
        return result


class WriterAgent(BaseAgent):
    """Transforms research findings into polished written content."""

    def __init__(self):
        super().__init__(AgentRole(
            "Writer",
            "Crafts clear, structured written content from research",
            ["write", "structure", "edit"]
        ))

    def process(self, task: Task) -> str:
        research = task.input_data
        lines = [l.strip() for l in research.split("\n") if l.strip() and not l.strip().startswith("Research on")]

        sections = {
            "Introduction": "This report examines the key aspects of the topic based on current research.",
            "Key Findings": "\n".join(f"  - {line}" for line in lines[:3]) if lines else "  - No findings available",
            "Analysis": "\n".join(f"  - {line}" for line in lines[3:]) if len(lines) > 3 else "  - Further investigation recommended",
            "Conclusion": "The research indicates significant developments in this area with practical applications across multiple domains.",
        }

        report = "=" * 50 + "\n"
        report += "  REPORT\n"
        report += "=" * 50 + "\n"
        for section, content in sections.items():
            report += f"\n  ## {section}\n  {content}\n"
        report += "\n" + "=" * 50

        self.work_log.append(f"Wrote report ({len(report)} chars)")
        task.output_data = report
        task.status = "completed"
        return report


class ReviewerAgent(BaseAgent):
    """Reviews content for quality, accuracy, and completeness."""

    def __init__(self):
        super().__init__(AgentRole(
            "Reviewer",
            "Evaluates content quality and provides actionable feedback",
            ["review", "critique", "score"]
        ))

    def process(self, task: Task) -> str:
        content = task.input_data
        scores = {}

        # Score different aspects
        scores["length"] = min(10, len(content) // 50)
        scores["structure"] = 8 if "##" in content else 4
        scores["content_depth"] = min(10, content.count("-") + content.count("."))
        scores["has_conclusion"] = 9 if "conclusion" in content.lower() else 3

        overall = sum(scores.values()) / len(scores)
        passed = overall >= 6.0

        review = f"Review Score: {overall:.1f}/10 ({'PASS' if passed else 'NEEDS REVISION'})\n"
        for aspect, score in scores.items():
            bar = "█" * score + "░" * (10 - score)
            review += f"  {aspect:20s} [{bar}] {score}/10\n"

        if not passed:
            review += "\n  Revision notes:\n"
            if scores["length"] < 6:
                review += "  - Content is too short, add more detail\n"
            if scores["structure"] < 6:
                review += "  - Add section headers for better organization\n"
            if scores["content_depth"] < 6:
                review += "  - Include more specific examples and data points\n"

        self.work_log.append(f"Reviewed ({overall:.1f}/10)")
        task.output_data = review
        task.status = "completed"
        return review


class TeamOrchestrator:
    """Manages the agent team and coordinates their work."""

    def __init__(self):
        self.agents = {
            "researcher": ResearcherAgent(),
            "writer": WriterAgent(),
            "reviewer": ReviewerAgent(),
        }
        self.task_log = []

    def execute_workflow(self, topic: str, max_revisions: int = 2):
        """Run the full research -> write -> review pipeline."""
        print(f"\n{'='*60}")
        print(f"  Team Workflow: '{topic}'")
        print(f"  Agents: {', '.join(a.role.name for a in self.agents.values())}")
        print(f"{'='*60}")

        # Step 1: Research
        print(f"\n  [1/3] Researcher gathering information...")
        research_task = Task(description="Research the topic", input_data=topic)
        research = self.agents["researcher"].process(research_task)
        print(f"  {research}")

        # Step 2: Write
        print(f"\n  [2/3] Writer creating report...")
        write_task = Task(description="Write report from research", input_data=research)
        report = self.agents["writer"].process(write_task)
        print(f"  {report}")

        # Step 3: Review loop
        for revision in range(max_revisions + 1):
            print(f"\n  [3/3] Reviewer evaluating (round {revision + 1})...")
            review_task = Task(description="Review the report", input_data=report)
            review = self.agents["reviewer"].process(review_task)
            print(f"  {review}")

            if "PASS" in review:
                print(f"\n  Report APPROVED after {revision + 1} review(s)!")
                break
            elif revision < max_revisions:
                print(f"  Sending back for revision...")
                # Writer revises based on feedback
                write_task = Task(description="Revise report", input_data=research + "\n\nFeedback:\n" + review)
                report = self.agents["writer"].process(write_task)

        # Summary
        print(f"\n{'='*60}")
        print(f"  Workflow Complete")
        print(f"{'='*60}")
        for name, agent in self.agents.items():
            print(f"  {agent.role.name}: {agent.work_log}")


if __name__ == "__main__":
    print("=== Role-Based Agent Team ===")

    team = TeamOrchestrator()
    team.execute_workflow("Multi-Agent Systems and Autonomous AI Agents")
