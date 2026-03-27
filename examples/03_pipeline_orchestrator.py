"""
Example 3: Pipeline Orchestrator with Supervisor
====================================================
A sequential pipeline where a supervisor agent manages the workflow,
delegates tasks, and can send work back for revision.

Run: python examples/03_pipeline_orchestrator.py
"""

from dataclasses import dataclass, field
from enum import Enum
import random


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVISION_NEEDED = "revision_needed"
    APPROVED = "approved"


@dataclass
class PipelineTask:
    name: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    input_data: dict = field(default_factory=dict)
    output_data: dict = field(default_factory=dict)
    attempts: int = 0
    max_attempts: int = 3
    feedback: str = ""


class WorkerAgent:
    """Base worker agent that processes tasks."""

    def __init__(self, name: str, skill: str):
        self.name = name
        self.skill = skill
        self.tasks_completed = 0

    def can_handle(self, task: PipelineTask) -> bool:
        return self.skill in task.name.lower()

    def execute(self, task: PipelineTask) -> PipelineTask:
        raise NotImplementedError


class DataCollector(WorkerAgent):
    """Collects and structures raw data."""

    def __init__(self):
        super().__init__("DataCollector", "collect")

    def execute(self, task: PipelineTask) -> PipelineTask:
        topic = task.input_data.get("topic", "general")
        quality = 0.6 + task.attempts * 0.15  # Gets better with revision

        data_points = [
            {"source": f"paper_{i}", "relevance": round(random.uniform(0.5, 1.0), 2),
             "summary": f"Key finding #{i} about {topic}"}
            for i in range(1, random.randint(4, 8))
        ]

        task.output_data = {
            "data_points": data_points,
            "coverage": round(quality, 2),
            "sources_checked": random.randint(10, 30) + task.attempts * 5,
        }
        task.status = TaskStatus.COMPLETED
        task.attempts += 1
        self.tasks_completed += 1
        return task


class Analyzer(WorkerAgent):
    """Analyzes collected data and extracts insights."""

    def __init__(self):
        super().__init__("Analyzer", "analyze")

    def execute(self, task: PipelineTask) -> PipelineTask:
        data = task.input_data.get("data_points", [])
        quality = 0.5 + task.attempts * 0.2

        insights = []
        for i, dp in enumerate(data[:5]):
            insights.append({
                "insight": f"Insight from {dp.get('source', 'unknown')}: Pattern detected",
                "confidence": round(min(1.0, dp.get("relevance", 0.5) + quality * 0.3), 2),
            })

        task.output_data = {
            "insights": insights,
            "analysis_depth": round(quality, 2),
            "data_quality_score": round(sum(d.get("relevance", 0) for d in data) / max(1, len(data)), 2),
        }
        task.status = TaskStatus.COMPLETED
        task.attempts += 1
        self.tasks_completed += 1
        return task


class ReportGenerator(WorkerAgent):
    """Generates final report from analysis."""

    def __init__(self):
        super().__init__("ReportGen", "report")

    def execute(self, task: PipelineTask) -> PipelineTask:
        insights = task.input_data.get("insights", [])
        quality = 0.55 + task.attempts * 0.2

        report_sections = ["Executive Summary", "Methodology", "Findings", "Recommendations"]
        report = {}
        for section in report_sections:
            if section == "Findings" and insights:
                report[section] = [ins["insight"] for ins in insights]
            else:
                report[section] = f"[{section} content with {len(insights)} data points]"

        task.output_data = {
            "report": report,
            "word_count": random.randint(500, 2000) + task.attempts * 300,
            "completeness": round(quality, 2),
        }
        task.status = TaskStatus.COMPLETED
        task.attempts += 1
        self.tasks_completed += 1
        return task


class SupervisorAgent:
    """Supervisor that manages the pipeline and ensures quality."""

    def __init__(self, quality_threshold: float = 0.7):
        self.quality_threshold = quality_threshold
        self.decisions = []

    def review(self, task: PipelineTask) -> tuple:
        """Review task output and decide: approve or revise."""
        output = task.output_data

        # Quality metrics vary by task type
        if "coverage" in output:
            quality = output["coverage"]
            metric_name = "coverage"
        elif "analysis_depth" in output:
            quality = output["analysis_depth"]
            metric_name = "analysis_depth"
        elif "completeness" in output:
            quality = output["completeness"]
            metric_name = "completeness"
        else:
            quality = 0.5
            metric_name = "default"

        approved = quality >= self.quality_threshold or task.attempts >= task.max_attempts

        decision = {
            "task": task.name,
            "quality": quality,
            "metric": metric_name,
            "approved": approved,
            "attempt": task.attempts,
        }
        self.decisions.append(decision)

        if approved:
            task.status = TaskStatus.APPROVED
            feedback = f"Approved ({metric_name}: {quality:.2f})"
        else:
            task.status = TaskStatus.REVISION_NEEDED
            feedback = f"Needs revision ({metric_name}: {quality:.2f} < {self.quality_threshold}). Please improve depth and coverage."

        task.feedback = feedback
        return approved, feedback


class PipelineOrchestrator:
    """Manages the full agent pipeline with supervisor oversight."""

    def __init__(self):
        self.workers = {
            "collect": DataCollector(),
            "analyze": Analyzer(),
            "report": ReportGenerator(),
        }
        self.supervisor = SupervisorAgent(quality_threshold=0.7)

    def run(self, topic: str):
        """Execute the full pipeline: collect -> analyze -> report."""
        print(f"\n{'='*60}")
        print(f"  Pipeline Orchestrator")
        print(f"  Topic: {topic}")
        print(f"  Quality Threshold: {self.supervisor.quality_threshold}")
        print(f"{'='*60}")

        pipeline_stages = [
            PipelineTask("collect_data", "Gather information on the topic",
                         input_data={"topic": topic}),
            PipelineTask("analyze_data", "Extract insights from collected data"),
            PipelineTask("report_generation", "Create final report from analysis"),
        ]

        previous_output = {}

        for stage_idx, task in enumerate(pipeline_stages):
            stage_name = task.name.replace("_", " ").title()
            print(f"\n  {'─'*50}")
            print(f"  Stage {stage_idx + 1}: {stage_name}")
            print(f"  {'─'*50}")

            # Inject previous stage output
            if previous_output:
                task.input_data.update(previous_output)

            # Find appropriate worker
            worker = None
            for skill, w in self.workers.items():
                if w.can_handle(task):
                    worker = w
                    break

            if not worker:
                print(f"  ERROR: No worker found for task '{task.name}'")
                continue

            # Execute with review loop
            while True:
                print(f"\n  [{worker.name}] Executing (attempt {task.attempts + 1}/{task.max_attempts})...")
                task = worker.execute(task)

                # Show output summary
                for key, val in task.output_data.items():
                    if isinstance(val, list):
                        print(f"    {key}: {len(val)} items")
                    elif isinstance(val, (int, float)):
                        print(f"    {key}: {val}")

                # Supervisor review
                approved, feedback = self.supervisor.review(task)
                print(f"  [Supervisor] {feedback}")

                if approved:
                    previous_output = task.output_data
                    break
                else:
                    # Reset for revision
                    task.status = TaskStatus.PENDING

        # Final summary
        print(f"\n{'='*60}")
        print(f"  Pipeline Complete")
        print(f"{'='*60}")
        print(f"\n  Worker Stats:")
        for name, worker in self.workers.items():
            print(f"    {worker.name}: {worker.tasks_completed} task executions")

        print(f"\n  Supervisor Decisions:")
        for d in self.supervisor.decisions:
            status = "APPROVED" if d["approved"] else "REVISION"
            print(f"    {d['task']}: {status} ({d['metric']}: {d['quality']:.2f}, attempt {d['attempt']})")

        # Display final report
        if pipeline_stages[-1].status == TaskStatus.APPROVED:
            report = pipeline_stages[-1].output_data.get("report", {})
            print(f"\n  Final Report ({pipeline_stages[-1].output_data.get('word_count', 0)} words):")
            for section, content in report.items():
                if isinstance(content, list):
                    print(f"    {section}:")
                    for item in content[:3]:
                        print(f"      - {item}")
                else:
                    print(f"    {section}: {content}")


if __name__ == "__main__":
    print("=== Pipeline Orchestrator with Supervisor ===")

    orchestrator = PipelineOrchestrator()
    orchestrator.run("Building Reliable Multi-Agent AI Systems")
