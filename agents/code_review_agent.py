"""Rule-based code review agent.

Consumes the structured output of RepositoryAnalysis.to_dict() and
produces a prioritized improvement plan.

- Follows the BaseAgent style of the other agents.
- Performs no file writes and modifies nothing automatically.
- ToolRegistry-compatible: exposes execute(plan) so it can be
  registered/executed like any tool without changes.
"""

from agents.base_agent import BaseAgent
from app.core.logger import AppLogger


SEVERITY_RANK = {
    "critical": 1,
    "warning": 2,
    "info": 3,
}

LARGE_FILE_LINES = 300


class CodeReviewAgent(BaseAgent):

    def __init__(self, memory=None):

        super().__init__(
            "Code Review Agent",
            memory
        )

        self.logger = AppLogger()

    # ------------------------------------------------------------------
    # BaseAgent / ToolRegistry entry points
    # ------------------------------------------------------------------

    def run(self, task):
        if isinstance(task, dict):
            return self.review(task)
        if hasattr(task, "to_dict"):
            return self.review(task.to_dict())
        if isinstance(task, str):
            return self._review_path(task)
        return self._empty_review(
            "Unsupported task. Provide a RepositoryAnalysis dict or a path."
        )

    def execute(self, plan):
        if not isinstance(plan, dict):
            return "Invalid review plan."
        if "analysis" in plan:
            return self.review(plan["analysis"])
        if "path" in plan:
            return self._review_path(plan["path"])
        return "Review plan requires 'analysis' or 'path'."

    # ------------------------------------------------------------------
    # Public review
    # ------------------------------------------------------------------

    def review(self, analysis):
        if not isinstance(analysis, dict):
            return self._empty_review(
                "Review requires a RepositoryAnalysis dictionary."
            )

        issues = (
            self._collect_wiring_issues(analysis)
            + self._collect_tool_issues(analysis)
            + self._collect_marker_issues(analysis)
            + self._collect_size_issues(analysis)
            + self._collect_overview_issues(analysis)
        )

        issues.sort(
            key=lambda issue: SEVERITY_RANK.get(
                issue["severity"], 99
            )
        )

        return {
            "summary": self._build_summary(analysis, issues),
            "issues": issues,
            "improvement_steps": self._build_steps(issues),
        }

    # ------------------------------------------------------------------
    # Review collectors
    # ------------------------------------------------------------------

    def _collect_wiring_issues(self, analysis):
        issues = []
        for check in analysis.get("wiring_checks", []) or []:
            if check.get("ok"):
                continue
            label = check.get("label", "Unknown check")
            file = check.get("file", "?")
            issues.append({
                "severity": "critical",
                "file": file,
                "problem": f"Architecture check failed: {label}",
                "recommendation": (
                    f"Inspect {file} and restore the wiring described "
                    "by the check."
                ),
                "source": "wiring_check",
            })
        return issues

    def _collect_tool_issues(self, analysis):
        issues = []
        for tool in analysis.get("tools", []) or []:
            if tool.get("has_execute"):
                continue
            file = f"tools/{tool.get('file', '?')}"
            issues.append({
                "severity": "critical",
                "file": file,
                "problem": "Tool does not implement execute(plan).",
                "recommendation": (
                    "Add an execute(plan) method that matches the "
                    "ToolAgent execution contract."
                ),
                "source": "tool_contract",
            })
        return issues

    def _collect_marker_issues(self, analysis):
        issues = []
        for marker in analysis.get("issues", []) or []:
            issues.append({
                "severity": "info",
                "file": marker.get("file", "?"),
                "problem": (
                    "TODO/FIXME/XXX marker at line "
                    f"{marker.get('line', '?')}: {marker.get('message', '')}"
                ),
                "recommendation": (
                    "Resolve the marker: implement, fix, or document "
                    "the remaining work."
                ),
                "source": "todo_marker",
            })
        return issues

    def _collect_size_issues(self, analysis):
        issues = []
        overview = analysis.get("overview", {}) or {}
        for item in overview.get("largest_files", []) or []:
            lines = item.get("lines", 0) or 0
            if lines < LARGE_FILE_LINES:
                continue
            issues.append({
                "severity": "warning",
                "file": item.get("file", "?"),
                "problem": f"File has grown to {lines} lines.",
                "recommendation": (
                    "Split the module into smaller focused units "
                    f"(target under {LARGE_FILE_LINES} lines)."
                ),
                "source": "file_size",
            })
        return issues

    def _collect_overview_issues(self, analysis):
        overview = analysis.get("overview", {}) or {}
        if overview.get("python_files"):
            return []
        return [{
            "severity": "critical",
            "file": overview.get("root", "?"),
            "problem": "Analysis found no Python files.",
            "recommendation": (
                "Verify the analyzed directory is the "
                "AI-Studio-Agent repository root."
            ),
            "source": "overview",
        }]

    # ------------------------------------------------------------------
    # Summary / steps
    # ------------------------------------------------------------------

    def _build_summary(self, analysis, issues):
        counts = {}
        for issue in issues:
            counts[issue["severity"]] = (
                counts.get(issue["severity"], 0) + 1
            )
        overview = analysis.get("overview", {}) or {}
        return (
            "Reviewed "
            f"{len(analysis.get('wiring_checks', []) or [])} wiring checks, "
            f"{len(analysis.get('tools', []) or [])} tools, "
            f"{overview.get('python_files', 0)} Python files, and "
            f"{len(analysis.get('issues', []) or [])} TODO/FIXME markers. "
            f"Found {len(issues)} issue(s): "
            f"{counts.get('critical', 0)} critical, "
            f"{counts.get('warning', 0)} warning(s), "
            f"{counts.get('info', 0)} info."
        )

    def _build_steps(self, issues):
        grouped = {}
        for issue in issues:
            grouped.setdefault(issue["severity"], []).append(issue)
        grouped = {
            severity: grouped[severity]
            for severity in ("critical", "warning", "info")
            if severity in grouped
        }

        steps = []
        for severity, group in grouped.items():
            files = sorted({issue["file"] for issue in group})
            targets = ", ".join(files[:5])
            if len(files) > 5:
                targets += f" (+{len(files) - 5} more)"
            actions = "; ".join(
                issue["recommendation"]
                for issue in group[:3]
            )
            steps.append({
                "priority": SEVERITY_RANK[severity],
                "severity": severity,
                "title": (
                    f"{severity.capitalize()}: resolve "
                    f"{len(group)} issue(s)"
                ),
                "description": f"Files: {targets}. {actions}",
            })
        return steps

    def _review_path(self, path):
        from tools.repository_analyzer import RepositoryAnalyzerTool

        result = RepositoryAnalyzerTool().analyze(path)
        if isinstance(result, str):
            return self._empty_review(result)
        return self.review(result.to_dict())

    @staticmethod
    def _empty_review(message):
        return {
            "summary": message,
            "issues": [],
            "improvement_steps": [],
        }
