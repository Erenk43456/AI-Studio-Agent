"""Human-readable rendering of a RepositoryAnalysis.

Keeps analysis data and presentation separated. The formatter only
reads a RepositoryAnalysis object and returns a text report, so the
data structures stay JSON-friendly for future agent consumers.
"""

from tools.repository_analysis import RepositoryAnalysis


class RepositoryReportFormatter:
    """Renders a RepositoryAnalysis into the classic text report."""

    MARKER_LIMIT = 15

    @staticmethod
    def render(analysis: RepositoryAnalysis) -> str:
        report = [
            "=" * 60,
            "AI-Studio-Agent Repository Analysis",
            "=" * 60,
            f"Generated: {analysis.generated_at}",
            "",
            "[1] Overview",
            RepositoryReportFormatter._render_overview(analysis.overview),
            "",
            "[2] Module Roles (architecture)",
            RepositoryReportFormatter._render_module_roles(analysis.module_roles),
            "",
            "[3] Key Definitions",
            RepositoryReportFormatter._render_definitions(analysis.definitions),
            "",
            "[4] Tool Registry",
            RepositoryReportFormatter._render_tools(
                analysis.tools,
                analysis.registry_names
            ),
            "",
            "[5] Architecture & Wiring Checks",
            RepositoryReportFormatter._render_wiring_checks(analysis.wiring_checks),
            "",
            "[6] TODO / FIXME Markers",
            RepositoryReportFormatter._render_issues(analysis.issues, RepositoryReportFormatter.MARKER_LIMIT),
            "",
            "=" * 60,
            "Analysis complete.",
            "=" * 60,
        ]
        return "\n".join(report)

    # ------------------------------------------------------------------
    # section renderers (each returns a string; data is never mutated)
    # ------------------------------------------------------------------

    @staticmethod
    def _render_overview(overview: dict) -> str:
        lines = []
        if overview.get("root"):
            lines.append(f"- Repository root: {overview['root']}")
        if overview.get("python_files") is not None:
            lines.append(f"- Python files: {overview['python_files']}")
        if overview.get("total_lines") is not None:
            lines.append(f"- Total lines: {overview['total_lines']}")
        if overview.get("top_level_modules"):
            lines.append(
                "- Top-level modules: "
                + ", ".join(overview["top_level_modules"])
            )
        if overview.get("largest_files"):
            lines.append(
                "- Largest files: "
                + ", ".join(
                    f"{item['file']} ({item['lines']} lines)"
                    for item in overview["largest_files"]
                )
            )
        return "\n".join(lines)

    @staticmethod
    def _render_module_roles(module_roles: dict) -> str:
        return "\n".join(
            f"- {rel}\n    -> {role}"
            for rel, role in module_roles.items()
        )

    @staticmethod
    def _render_definitions(definitions: dict) -> str:
        sections = []
        for rel in definitions:
            defs = definitions[rel]
            if not defs:
                continue
            sections.append(f"- {rel}:")
            sections.append("    " + ", ".join(defs))
        return "\n".join(sections)

    @staticmethod
    def _render_tools(tools: list, registry_names: list) -> str:
        if not tools:
            return "tools/ directory not found."
        lines = ["Registered tool implementations (tools/):"]
        for tool in tools:
            status = "execute(): OK" if tool["has_execute"] else "execute(): MISSING"
            lines.append(f"- {tool['file']}: {status}")
        if registry_names:
            lines.append(
                "\nRegistered names in AIContainer: "
                + ", ".join(registry_names)
            )
        return "\n".join(lines)

    @staticmethod
    def _render_wiring_checks(wiring_checks: list) -> str:
        return "\n".join(
            f"- [{'OK' if check['ok'] else 'FAIL'}] {check['label']}"
            for check in wiring_checks
        )

    @staticmethod
    def _render_issues(issues: list, limit: int) -> str:
        if not issues:
            return "- No TODO/FIXME markers found."
        return "\n".join(
            f"- {issue['file']}:{issue['line']}: {issue['message']}"
            for issue in issues[:limit]
        )
