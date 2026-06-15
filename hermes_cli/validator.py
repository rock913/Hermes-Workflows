"""Schema validation for Hermes workflow YAML templates."""

import re
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    path: str
    message: str


@dataclass
class ValidationReport:
    file: str
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


KNOWN_TOOLS = {
    # SROS MCP tools
    "sros-db-query",
    "sros-hpc-submit",
    "sros-hpc-status",
    "sros-hpc-cancel",
    "sros-data-run-script",
    "sros-manuscript-insert",
    "sros-scholar-search",
    # ARC MCP tools — DW5 (current)
    "arc-mcp-impact",
    "arc-mcp-context",
    "arc-mcp-paths",
    "arc-data-wiki-read",
    # ARC MCP tools — pre-DW5 (backward compat, templates still reference these)
    "arc-wiki-read",
    "arc-graph-query",
    "arc-wiki-impact",
    "arc-wiki-paths",
    # Built-in
    "python-eval",
    "file-writer",
}

KNOWN_MODELS = {
    "claude-sonnet-4-6",
    "claude-opus-4-7",
    "claude-haiku-4-5",
}

VALID_WORKFLOW_TYPES = {
    "sequential",
    "sequential_with_feedback",
    "parallel",
    "dag",
}


def validate_template(data: dict, filepath: str) -> ValidationReport:
    report = ValidationReport(file=filepath)
    _check_top_level(data, report)
    _check_agents(data.get("agents", []), report)
    _check_workflow(data.get("workflow", {}), data.get("agents", []), report)
    _check_cross_refs(data, report)
    return report


def _check_top_level(data: dict, report: ValidationReport):
    for field in ["name", "description", "version", "agents", "workflow"]:
        if field not in data:
            report.errors.append(
                ValidationError("", f"Missing required top-level field: '{field}'")
            )
    if not isinstance(data.get("agents"), list):
        report.errors.append(ValidationError("agents", "Must be a list"))
    if not isinstance(data.get("workflow"), dict):
        report.errors.append(ValidationError("workflow", "Must be a mapping"))


def _check_agents(agents: list, report: ValidationReport):
    if not agents:
        report.errors.append(ValidationError("agents", "At least one agent is required"))
        return
    agent_names = set()
    for i, agent in enumerate(agents):
        prefix = f"agents[{i}]"
        name = agent.get("name")
        if not name:
            report.errors.append(ValidationError(prefix, "Missing 'name'"))
            continue
        if name in agent_names:
            report.errors.append(ValidationError(f"{prefix}.name", f"Duplicate agent name: '{name}'"))
        agent_names.add(name)
        if "role" not in agent:
            report.warnings.append(ValidationError(f"{prefix}", "Missing 'role' description"))
        if agent.get("model") and agent["model"] not in KNOWN_MODELS:
            report.warnings.append(
                ValidationError(f"{prefix}.model", f"Unknown model '{agent['model']}'")
            )
        for j, tool in enumerate(agent.get("tools", [])):
            if tool not in KNOWN_TOOLS:
                report.warnings.append(
                    ValidationError(f"{prefix}.tools[{j}]", f"Unknown tool: '{tool}'")
                )
        state = agent.get("state", {})
        if isinstance(state, dict):
            if state.get("persist") not in (True, False, None):
                report.warnings.append(
                    ValidationError(f"{prefix}.state.persist", "Should be boolean")
                )


def _check_workflow(wf: dict, agents: list, report: ValidationReport):
    if not isinstance(wf, dict):
        return
    agent_names = {a.get("name") for a in agents}
    wf_type = wf.get("type")
    if wf_type and wf_type not in VALID_WORKFLOW_TYPES:
        report.warnings.append(
            ValidationError("workflow.type", f"Unknown workflow type: '{wf_type}'")
        )
    if "global_timeout_hours" not in wf:
        report.warnings.append(
            ValidationError("workflow", "Missing 'global_timeout_hours'")
        )
    steps = wf.get("steps", [])
    if not steps:
        report.errors.append(ValidationError("workflow.steps", "At least one step is required"))
        return
    step_ids = set()
    for i, step in enumerate(steps):
        prefix = f"workflow.steps[{i}]"
        sid = step.get("id")
        if not sid:
            report.errors.append(ValidationError(prefix, "Missing 'id'"))
            continue
        if sid in step_ids:
            report.errors.append(ValidationError(f"{prefix}.id", f"Duplicate step id: '{sid}'"))
        step_ids.add(sid)
        if "agent" not in step:
            report.errors.append(ValidationError(prefix, "Missing 'agent'"))
        elif step["agent"] not in agent_names:
            report.errors.append(
                ValidationError(f"{prefix}.agent", f"Agent '{step['agent']}' not defined")
            )
        if "task" not in step:
            report.errors.append(ValidationError(prefix, "Missing 'task'"))
        if "timeout_hours" not in step:
            report.warnings.append(ValidationError(prefix, "Missing 'timeout_hours'"))
        for dep in step.get("depends_on", []):
            if not isinstance(dep, str):
                continue
            m = re.match(r"^(\w+)", dep)
            if m and m.group(1) not in step_ids:
                pass  # depends_on may reference steps defined earlier — checked in _check_cross_refs
        fb = step.get("feedback_to")
        if fb and fb not in step_ids:
            pass  # same as above
        max_loops = step.get("max_feedback_loops")
        if max_loops is not None and step.get("feedback_to") is None:
            report.warnings.append(
                ValidationError(prefix, "max_feedback_loops set but no feedback_to")
            )


def _check_cross_refs(data: dict, report: ValidationReport):
    steps = data.get("workflow", {}).get("steps", [])
    step_ids = {s["id"] for s in steps if "id" in s}
    for step in steps:
        sid = step.get("id", "?")
        for dep in step.get("depends_on", []):
            if dep not in step_ids:
                report.errors.append(
                    ValidationError(
                        f"workflow.steps[{sid}].depends_on",
                        f"References undefined step: '{dep}'",
                    )
                )
        fb = step.get("feedback_to")
        if fb and fb not in step_ids:
            report.errors.append(
                ValidationError(
                    f"workflow.steps[{sid}].feedback_to",
                    f"References undefined step: '{fb}'",
                )
            )
