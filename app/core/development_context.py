import json
import re
from pathlib import Path

from app.core.logger import AppLogger


class DevelopmentContext:

    def __init__(
        self,
        project_memory,
        workspace
    ):

        self.project_memory = project_memory
        self.workspace = Path(workspace)

        self.logger = AppLogger()

        # Memory loading state.
        #
        # This is deliberately tracked separately from the
        # returned dictionaries because an empty memory and a
        # failed memory lookup are both different from having
        # usable project memory.
        self._memory_available = False

    # =============================================================
    # Public API
    # =============================================================

    def build(
        self,
        task
    ):

        task = str(task or "").strip()

        # Reset memory state for every build.
        self._memory_available = False

        targets = self.extract_target_files(
            task
        )

        architecture = self.get_architecture()

        all_files = self.get_all_files()

        target_files = self.collect_target_files(
            targets,
            all_files
        )

        related_files = self.find_related_files(
            task,
            targets,
            all_files,
            architecture
        )

        relationships = self.build_relationships(
            targets,
            target_files,
            related_files,
            architecture
        )

        strategy = self.determine_strategy(
            task,
            targets,
            target_files,
            related_files,
            relationships,
            architecture
        )

        context = {
            "task": task,

            "targets": targets,

            "target_files": target_files,

            "related_files": related_files,

            "relationships": relationships,

            "architecture": architecture,

            "strategy": strategy
        }

        self.logger.info(
            f"Development context built: "
            f"{len(targets)} target(s), "
            f"{len(related_files)} related file(s), "
            f"strategy={strategy['type']}"
        )

        return context

    # =============================================================
    # Target detection
    # =============================================================

    def extract_target_files(
        self,
        task
    ):

        if not task:
            return []

        candidates = re.findall(
            r"""
            (?:
                [A-Za-z0-9_.-]+[\\/] 
            )*
            [A-Za-z0-9_.-]+\.py
            """,
            task,
            re.VERBOSE
        )

        result = []

        for candidate in candidates:

            candidate = candidate.replace(
                "\\",
                "/"
            )

            # Remove only an actual leading "./" or ".\".
            while candidate.startswith("./"):
                candidate = candidate[2:]

            if candidate.startswith("/"):
                candidate = candidate.lstrip("/")

            if candidate not in result:
                result.append(candidate)

        return result

    # =============================================================
    # Project memory
    # =============================================================

    def get_all_files(
        self
    ):

        try:

            files = (
                self.project_memory.get_all_files()
            )

        except Exception as error:

            self.logger.error(
                f"Failed to load project files from memory: "
                f"{error}"
            )

            return {}

        if not isinstance(
            files,
            dict
        ):

            return {}

        if files:
            self._memory_available = True

        return files

    def collect_target_files(
        self,
        targets,
        all_files
    ):

        result = {}

        for target in targets:

            info = None

            if isinstance(
                all_files,
                dict
            ):

                info = all_files.get(
                    target
                )

                if info is None:

                    normalized_target = (
                        target.replace(
                            "\\",
                            "/"
                        )
                    )

                    for path, value in all_files.items():

                        normalized_path = str(
                            path
                        ).replace(
                            "\\",
                            "/"
                        )

                        if normalized_path == normalized_target:

                            info = value
                            break

            if info is None:

                try:

                    info = self.project_memory.get_file(
                        target
                    )

                except Exception as error:

                    self.logger.error(
                        f"Failed to load target file "
                        f"{target} from memory: {error}"
                    )

            if info is not None:

                self._memory_available = True

                result[target] = info

        return result

    # =============================================================
    # Architecture
    # =============================================================

    def get_architecture(
        self
    ):

        try:

            architecture = (
                self.project_memory.get_architecture()
            )

            if not isinstance(
                architecture,
                dict
            ):

                return {}

            if architecture:
                self._memory_available = True

            return architecture

        except Exception as error:

            self.logger.error(
                f"Failed to load project architecture "
                f"from memory: {error}"
            )

            return {}

    # =============================================================
    # Related files
    # =============================================================

    def find_related_files(
        self,
        task,
        targets,
        all_files,
        architecture=None
    ):

        if not isinstance(
            all_files,
            dict
        ):

            return {}

        architecture = (
            architecture
            if isinstance(
                architecture,
                dict
            )
            else {}
        )

        related = {}

        task_words = self._task_words(
            task
        )

        target_paths = []

        for target in targets:

            target_paths.append(
                Path(target)
            )

        for path, info in all_files.items():

            normalized = str(
                path
            ).replace(
                "\\",
                "/"
            )

            # Never duplicate target files.
            if normalized in targets:

                continue

            path_obj = Path(
                normalized
            )

            score = 0

            reasons = []

            relationships = []

            lower_path = normalized.lower()

            # -----------------------------------------------------
            # Same package / directory
            # -----------------------------------------------------

            for target_path in target_paths:

                if path_obj.parent == target_path.parent:

                    score += 5

                    reasons.append(
                        "same package or directory"
                    )

                    relationships.append(
                        "same_package"
                    )

            # -----------------------------------------------------
            # Same module concept
            # -----------------------------------------------------

            for target_path in target_paths:

                target_stem = (
                    target_path.stem.lower()
                )

                stem = (
                    path_obj.stem.lower()
                )

                if (
                    target_stem
                    and target_stem in stem
                ) or (
                    stem
                    and stem in target_stem
                ):

                    score += 3

                    reasons.append(
                        "related module name"
                    )

                    relationships.append(
                        "related_module"
                    )

            # -----------------------------------------------------
            # Task words in path
            # -----------------------------------------------------

            for word in task_words:

                if word in lower_path:

                    score += 2

                    reasons.append(
                        f"task word in path: {word}"
                    )

            # -----------------------------------------------------
            # Project memory information
            # -----------------------------------------------------

            serialized = self.serialize_info(
                info
            )

            for word in task_words:

                if (
                    len(word) >= 4
                    and word in serialized
                ):

                    score += 1

                    reasons.append(
                        f"task concept in memory: {word}"
                    )

            # -----------------------------------------------------
            # Architecture relationships
            # -----------------------------------------------------

            (
                architecture_score,
                architecture_reasons,
                architecture_relationships
            ) = self.score_architecture_relationship(
                normalized,
                targets,
                architecture,
                info
            )

            score += architecture_score

            reasons.extend(
                architecture_reasons
            )

            relationships.extend(
                architecture_relationships
            )

            # -----------------------------------------------------
            # Explicit dependency information
            # -----------------------------------------------------

            (
                dependency_score,
                dependency_reasons,
                dependency_relationships
            ) = self.score_dependency_relationship(
                normalized,
                targets,
                info
            )

            score += dependency_score

            reasons.extend(
                dependency_reasons
            )

            relationships.extend(
                dependency_relationships
            )

            # A file must have a meaningful relationship before
            # entering the development context.
            #
            # Architecture-layer membership by itself is not
            # enough. This prevents unrelated files such as
            # app/tools.py from being included merely because
            # they live under app/.
            meaningful_relationships = {
                "same_package",
                "related_module",
                "references_target",
                "references_target_file",
                "references_target_module",
                "target_references_file",
                "target_references_module",
                "architecture_member",
                "architecture_reference"
            }

            has_meaningful_relationship = bool(
                set(relationships)
                & meaningful_relationships
            )

            if not has_meaningful_relationship:
                continue

            # Remove duplicate information while
            # preserving order.

            reasons = list(
                dict.fromkeys(
                    reasons
                )
            )

            relationships = list(
                dict.fromkeys(
                    relationships
                )
            )

            related[normalized] = {
                "score": score,
                "reasons": reasons,
                "relationships": relationships,
                "info": info
            }

        ordered = sorted(
            related.items(),
            key=lambda item: item[1]["score"],
            reverse=True
        )

        # Keep development context bounded.
        return dict(
            ordered[:12]
        )

    # =============================================================
    # Architecture relationship scoring
    # =============================================================

    def score_architecture_relationship(
        self,
        path,
        targets,
        architecture,
        info
    ):

        score = 0

        reasons = []

        relationships = []

        architecture_text = self.serialize_info(
            architecture
        )

        path_lower = path.lower()

        # ---------------------------------------------------------
        # Direct path references
        # ---------------------------------------------------------

        for target in targets:

            target_normalized = (
                target.replace(
                    "\\",
                    "/"
                ).lower()
            )

            target_name = Path(
                target_normalized
            ).name.lower()

            if (
                target_normalized in architecture_text
                and path_lower in architecture_text
            ):

                score += 8

                reasons.append(
                    "both files appear in project architecture"
                )

                relationships.append(
                    "architecture_member"
                )

            elif (
                target_name
                and target_name in architecture_text
                and path_lower in architecture_text
            ):

                score += 4

                reasons.append(
                    "architecture references target and related file"
                )

                relationships.append(
                    "architecture_reference"
                )

        # ---------------------------------------------------------
        # Layer / component information
        #
        # Only consider architecture layers when the architecture
        # actually contains structural information. Merely having
        # "app" or "core" in a path must not make every file
        # architecture-related.
        # ---------------------------------------------------------

        if architecture:

            path_parts = set(
                part.lower()
                for part in Path(path).parts
            )

            architecture_keywords = (
                "agent",
                "agents",
                "orchestrator",
                "orchestrators",
                "container",
                "containers",
                "tool",
                "tools",
                "memory",
                "model",
                "models",
                "app",
                "core"
            )

            matching_layers = (
                path_parts
                &
                set(architecture_keywords)
            )

            if matching_layers:

                # Layer membership is supporting evidence only.
                score += 1

                reasons.append(
                    "belongs to known project architecture layer"
                )

                relationships.append(
                    "architecture_layer"
                )

        return (
            score,
            reasons,
            relationships
        )

    # =============================================================
    # Dependency relationship scoring
    # =============================================================

    def score_dependency_relationship(
        self,
        path,
        targets,
        info
    ):

        score = 0

        reasons = []

        relationships = []

        serialized = self.serialize_info(
            info
        )

        for target in targets:

            target_normalized = (
                target.replace(
                    "\\",
                    "/"
                ).lower()
            )

            target_stem = Path(
                target_normalized
            ).stem.lower()

            target_name = Path(
                target_normalized
            ).name.lower()

            # -----------------------------------------------------
            # Direct target path reference
            # -----------------------------------------------------

            if target_normalized in serialized:

                score += 7

                reasons.append(
                    f"memory references target: {target}"
                )

                relationships.append(
                    "references_target"
                )

            # -----------------------------------------------------
            # Target filename reference
            # -----------------------------------------------------

            elif (
                target_name
                and target_name in serialized
            ):

                score += 5

                reasons.append(
                    f"memory references target file: {target_name}"
                )

                relationships.append(
                    "references_target_file"
                )

            # -----------------------------------------------------
            # Target module reference
            # -----------------------------------------------------

            elif (
                target_stem
                and target_stem in serialized
            ):

                score += 3

                reasons.append(
                    f"memory references target module: {target_stem}"
                )

                relationships.append(
                    "references_target_module"
                )

        # ---------------------------------------------------------
        # Target may reference this file.
        # ---------------------------------------------------------

        for target in targets:

            target_info = None

            try:

                target_info = (
                    self.project_memory.get_file(
                        target
                    )
                )

            except Exception:

                target_info = None

            if target_info is None:

                continue

            target_serialized = self.serialize_info(
                target_info
            )

            normalized_path = (
                path.replace(
                    "\\",
                    "/"
                ).lower()
            )

            filename = Path(
                normalized_path
            ).name.lower()

            stem = Path(
                normalized_path
            ).stem.lower()

            if normalized_path in target_serialized:

                score += 8

                reasons.append(
                    f"target memory references related file: {path}"
                )

                relationships.append(
                    "target_references_file"
                )

            elif (
                filename
                and filename in target_serialized
            ):

                score += 5

                reasons.append(
                    f"target references related file: {filename}"
                )

                relationships.append(
                    "target_references_file"
                )

            elif (
                stem
                and stem in target_serialized
            ):

                score += 3

                reasons.append(
                    f"target references related module: {stem}"
                )

                relationships.append(
                    "target_references_module"
                )

        return (
            score,
            reasons,
            relationships
        )

    # =============================================================
    # Relationship graph
    # =============================================================

    def build_relationships(
        self,
        targets,
        target_files,
        related_files,
        architecture
    ):

        relationships = {}

        for target in targets:

            target_relationships = []

            target_info = target_files.get(
                target,
                {}
            )

            target_serialized = self.serialize_info(
                target_info
            )

            for related_path, related_info in related_files.items():

                metadata = related_info

                relation_types = metadata.get(
                    "relationships",
                    []
                )

                reasons = metadata.get(
                    "reasons",
                    []
                )

                relationship = {
                    "file": related_path,
                    "types": relation_types,
                    "reasons": reasons,
                    "score": metadata.get(
                        "score",
                        0
                    )
                }

                if (
                    relation_types
                    or
                    related_path.lower()
                    in target_serialized
                ):

                    target_relationships.append(
                        relationship
                    )

            relationships[target] = (
                target_relationships
            )

        return relationships

    # =============================================================
    # Development strategy
    # =============================================================

    def determine_strategy(
        self,
        task,
        targets,
        target_files,
        related_files,
        relationships,
        architecture
    ):

        text = task.lower()

        relationship_count = sum(
            len(value)
            for value in relationships.values()
        )

        architecture_text = self.serialize_info(
            architecture
        )

        # ---------------------------------------------------------
        # Explicit analysis requests
        # ---------------------------------------------------------

        if self.contains_any(
            text,
            (
                "analiz",
                "incele",
                "analyze",
                "inspect",
                "araştır",
                "bak"
            )
        ):

            strategy_type = "analysis"

            phases = [
                "inspect_memory",
                "inspect_target",
                "inspect_architecture",
                "inspect_dependencies",
                "produce_analysis"
            ]

        # ---------------------------------------------------------
        # Refactoring
        # ---------------------------------------------------------

        elif self.contains_any(
            text,
            (
                "refactor",
                "refactoring",
                "yeniden düzenle",
                "yeniden yapılandır",
                "temizle"
            )
        ):

            strategy_type = (
                "architecture_preserving_refactor"
            )

            phases = [
                "inspect_memory",
                "inspect_target",
                "inspect_dependencies",
                "identify_architecture_constraints",
                "design_minimal_change",
                "refactor_minimally",
                "validate"
            ]

        # ---------------------------------------------------------
        # Bug fixing
        # ---------------------------------------------------------

        elif self.contains_any(
            text,
            (
                "hata",
                "hataları",
                "hata düzelt",
                "bug",
                "error",
                "fix",
                "düzelt"
            )
        ):

            # A related file is enough to make the fix
            # architecture-aware. Requiring three relationship
            # edges was too strict and caused valid architectural
            # contexts to fall back to targeted_fix.
            if related_files:

                strategy_type = (
                    "architecture_aware_targeted_fix"
                )

                phases = [
                    "inspect_memory",
                    "inspect_target",
                    "inspect_related_files",
                    "identify_root_cause",
                    "identify_architecture_constraints",
                    "apply_minimal_fix",
                    "validate"
                ]

            else:

                strategy_type = "targeted_fix"

                phases = [
                    "inspect_memory",
                    "inspect_target",
                    "inspect_dependencies",
                    "identify_root_cause",
                    "apply_minimal_fix",
                    "validate"
                ]

        # ---------------------------------------------------------
        # Feature implementation
        # ---------------------------------------------------------

        elif self.contains_any(
            text,
            (
                "ekle",
                "oluştur",
                "implement",
                "implement et",
                "özellik",
                "feature",
                "add",
                "yeni"
            )
        ):

            if related_files:

                strategy_type = (
                    "architecture_aware_feature_implementation"
                )

                phases = [
                    "inspect_memory",
                    "inspect_architecture",
                    "identify_integration_points",
                    "inspect_related_files",
                    "design_minimal_change",
                    "implement",
                    "validate"
                ]

            else:

                strategy_type = "feature_implementation"

                phases = [
                    "inspect_memory",
                    "inspect_architecture",
                    "identify_integration_points",
                    "design_minimal_change",
                    "implement",
                    "validate"
                ]

        # ---------------------------------------------------------
        # Default architecture-aware development
        # ---------------------------------------------------------

        else:

            strategy_type = (
                "architecture_aware_development"
            )

            phases = [
                "inspect_memory",
                "identify_targets",
                "inspect_architecture",
                "inspect_dependencies",
                "identify_integration_points",
                "choose_minimal_change",
                "implement",
                "validate"
            ]

        # ---------------------------------------------------------
        # Determine whether repository analysis is needed.
        # ---------------------------------------------------------

        memory_available = self._memory_available

        repository_analysis_fallback = (
            not memory_available
        )

        # ---------------------------------------------------------
        # Multiple targets require broader planning.
        # ---------------------------------------------------------

        multi_target = (
            len(targets) > 1
        )

        if multi_target and strategy_type == "targeted_fix":

            strategy_type = (
                "multi_target_targeted_fix"
            )

            phases = [
                "inspect_memory",
                "inspect_targets",
                "inspect_dependencies",
                "identify_root_cause",
                "coordinate_changes",
                "apply_minimal_fix",
                "validate"
            ]

        return {
            "type": strategy_type,

            "phases": phases,

            "target_count": len(
                targets
            ),

            "related_file_count": len(
                related_files
            ),

            "relationship_count": relationship_count,

            "memory_first": True,

            "memory_available": memory_available,

            "repository_analysis_fallback": (
                repository_analysis_fallback
            ),

            "architecture_aware": True,

            "architecture_preserving": True,

            "minimal_change": True,

            "multi_target": multi_target
        }

    # =============================================================
    # Prompt representation
    # =============================================================

    def to_prompt(
        self,
        context
    ):

        if not isinstance(
            context,
            dict
        ):

            return "{}"

        safe_context = dict(
            context
        )

        return json.dumps(
            safe_context,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    # =============================================================
    # Utilities
    # =============================================================

    def serialize_info(
        self,
        info
    ):

        try:

            return json.dumps(
                info,
                ensure_ascii=False,
                default=str
            ).lower()

        except Exception:

            return str(
                info
            ).lower()

    def contains_any(
        self,
        text,
        words
    ):

        return any(
            word in text
            for word in words
        )

    def _task_words(
        self,
        task
    ):

        words = re.findall(
            r"[A-Za-z0-9_]+",
            task.lower()
        )

        ignored = {
            "dosya",
            "dosyasındaki",
            "dosyasını",
            "dosyadaki",
            "hataları",
            "düzelt",
            "fix",
            "the",
            "in",
            "and",
            "with",
            "file",
            "python",
            "kod",
            "kodu",
            "için",
            "bir",
            "bu",
            "şu",
            "olan",
            "olarak",
            "üzerinde"
        }

        return {
            word
            for word in words
            if len(word) >= 3
            and word not in ignored
        }