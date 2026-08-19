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

                if self._contains_word(
                    lower_path,
                    word
                ):

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
                    and self._contains_word(
                        serialized,
                        word
                    )
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

            relationship_set = set(
                relationships
            )

            # A file must have a meaningful relationship before
            # entering the development context.
            #
            # Architecture-layer membership by itself is not
            # enough. This prevents unrelated files such as
            # app/tools.py from being included merely because
            # they live under app/.

            explicit_relationships = {
                "references_target",
                "references_target_file",
                "references_target_module",
                "target_references_file",
                "target_references_module",
                "architecture_member",
                "architecture_reference"
            }

            has_explicit_relationship = bool(
                relationship_set
                & explicit_relationships
            )

            has_structural_relationship = (
                "same_package" in relationship_set
                and "related_module" in relationship_set
            )

            has_meaningful_relationship = (
                has_explicit_relationship
                or has_structural_relationship
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

        if not isinstance(
            architecture,
            dict
        ):

            return (
                score,
                reasons,
                relationships
            )

        normalized_path = (
            str(path)
            .replace("\\", "/")
            .lower()
        )

        target_paths = [
            str(target)
            .replace("\\", "/")
            .lower()
            for target in targets
        ]

        # =========================================================
        # Explicit architecture collections
        # =========================================================

        explicit_membership_keys = {
            "files",
            "components",
            "modules",
            "services",
            "packages",
            "nodes",
            "entries",
        }

        def collect_paths(
            value
        ):

            result = []

            if isinstance(
                value,
                str
            ):

                normalized = (
                    value
                    .replace(
                        "\\",
                        "/"
                    )
                    .lower()
                    .strip()
                )

                if normalized.endswith(
                    ".py"
                ):

                    result.append(
                        normalized
                    )

            elif isinstance(
                value,
                (list, tuple, set)
            ):

                for item in value:

                    result.extend(
                        collect_paths(
                            item
                        )
                    )

            elif isinstance(
                value,
                dict
            ):

                for item in value.values():

                    result.extend(
                        collect_paths(
                            item
                        )
                    )

            return result

        explicit_members = set()

        for key in explicit_membership_keys:

            if key in architecture:

                explicit_members.update(
                    collect_paths(
                        architecture[key]
                    )
                )

        # =========================================================
        # Explicit architecture membership
        # =========================================================

        if normalized_path in explicit_members:

            for target in targets:

                target_normalized = (
                    target
                    .replace(
                        "\\",
                        "/"
                    )
                    .lower()
                    .strip()
                )

                if target_normalized in explicit_members:

                    score += 8

                    reasons.append(
                        "both files appear in project architecture"
                    )

                    relationships.append(
                        "architecture_member"
                    )

                    break

        # =========================================================
        # Architecture layer information
        #
        # IMPORTANT:
        #
        # Same layer alone is NOT meaningful.
        #
        # A candidate in the same layer can become related only
        # when its own memory contains a meaningful integration,
        # dependency, usage, interface, or implementation signal,
        # or explicitly mentions the target.
        # =========================================================

        layer_memberships = []

        layers = architecture.get(
            "layers"
        )

        if isinstance(
            layers,
            dict
        ):

            for layer_name, members in layers.items():

                member_paths = set(
                    collect_paths(
                        members
                    )
                )

                if normalized_path in member_paths:

                    layer_memberships.append(
                        (
                            str(
                                layer_name
                            ).lower(),
                            member_paths
                        )
                    )

        info_text = self.serialize_info(
            info
        )

        # These are semantic indicators, but they must be matched
        # as complete words/phrases rather than arbitrary substrings.
        #
        # This is important because:
        #
        #     "unrelated module"
        #
        # must NOT match:
        #
        #     "related"
        #
        # simply because "related" is contained inside "unrelated".

        semantic_indicators = {
            "integration",
            "dependency",
            "depends",
            "used by",
            "used_by",
            "uses",
            "imports",
            "import",
            "related",
            "connection",
            "connects",
            "connect",
            "pipeline",
            "interface",
            "implementation",
        }

        for target in targets:

            target_normalized = (
                target
                .replace(
                    "\\",
                    "/"
                )
                .lower()
                .strip()
            )

            target_stem = Path(
                target_normalized
            ).stem.lower()

            target_name = Path(
                target_normalized
            ).name.lower()

            same_layer = False

            for _, member_paths in layer_memberships:

                if target_normalized in member_paths:

                    same_layer = True

                    break

            if not same_layer:

                continue

            # -----------------------------------------------------
            # Match semantic indicators safely.
            #
            # Single-word indicators use word boundaries.
            # Multi-word indicators are matched as normalized
            # phrases.
            # -----------------------------------------------------

            has_semantic_indicator = (
                self._contains_any_semantic_indicator(
                    info_text,
                    semantic_indicators
                )
            )

            mentions_target = (
                target_normalized in info_text
                or self._contains_word(
                    info_text,
                    target_name
                )
                or self._contains_word(
                    info_text,
                    target_stem
                )
            )

            if (
                has_semantic_indicator
                or mentions_target
            ):

                score += 6

                reasons.append(
                    "architecture layer contains a semantically related file"
                )

                relationships.append(
                    "architecture_member"
                )

                break

        # =========================================================
        # Architecture layer is supporting evidence only.
        # =========================================================

        path_parts = {
            part.lower()
            for part in Path(
                normalized_path
            ).parts
        }

        architecture_keywords = {
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
        }

        if (
            path_parts
            &
            architecture_keywords
        ):

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
                target
                .replace(
                    "\\",
                    "/"
                )
                .lower()
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
                and self._contains_word(
                    serialized,
                    target_stem
                )
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
                path
                .replace(
                    "\\",
                    "/"
                )
                .lower()
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
                and self._contains_word(
                    target_serialized,
                    stem
                )
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

        if (
            multi_target
            and strategy_type == "targeted_fix"
        ):

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

    def _contains_word(
        self,
        text,
        word
    ):
        """
        Check whether a word/token exists as a complete word.

        This prevents false positives such as:

            related -> unrelated
            app     -> application
            core    -> hardcore
        """

        if not text or not word:
            return False

        text = str(text).lower()
        word = str(word).lower().strip()

        if not word:
            return False

        # Paths and identifiers can contain /, _, -, and dots.
        # For ordinary semantic words, boundaries are enough.
        #
        # The negative look-arounds prevent matching the word
        # inside larger alphabetic/number/underscore identifiers.

        pattern = (
            rf"(?<![a-z0-9_])"
            rf"{re.escape(word)}"
            rf"(?![a-z0-9_])"
        )

        return re.search(
            pattern,
            text,
            re.IGNORECASE
        ) is not None

    def _contains_any_semantic_indicator(
        self,
        text,
        indicators
    ):
        """
        Safely detect semantic relationship indicators.

        Single-word indicators are matched as complete words.
        Multi-word indicators are matched as phrases.

        This intentionally avoids substring matching so that:

            "unrelated"

        does not satisfy:

            "related"
        """

        if not text:
            return False

        normalized_text = str(
            text
        ).lower()

        for indicator in indicators:

            indicator = str(
                indicator
            ).lower().strip()

            if not indicator:
                continue

            # Multi-word phrases such as:
            #
            #   used by
            #   used_by
            #
            # are normalized and matched as phrases.

            if " " in indicator:

                phrase_pattern = (
                    rf"(?<![a-z0-9_])"
                    rf"{re.escape(indicator)}"
                    rf"(?![a-z0-9_])"
                )

                if re.search(
                    phrase_pattern,
                    normalized_text,
                    re.IGNORECASE
                ):

                    return True

            else:

                if self._contains_word(
                    normalized_text,
                    indicator
                ):

                    return True

        return False

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
            "üzerinde",
            "add",
            "a",
            "feature",
            "to",
            "implement",
            "implementation",
            "new",
            "work",
            "on",
            "inspect",
            "analyze",
            "refactor",
            "bug",
            "error",
        }

        # ---------------------------------------------------------
        # Python file paths mentioned in the task are targets,
        # not semantic task concepts.
        #
        # Example:
        #
        #   "Fix app/core/parser.py"
        #
        # must not produce:
        #
        #   app
        #   core
        #   parser
        #   py
        #
        # Otherwise unrelated files can become related merely
        # because they share a directory name.
        # ---------------------------------------------------------

        path_words = set()

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

        for candidate in candidates:

            normalized = candidate.replace(
                "\\",
                "/"
            )

            path_without_extension = (
                normalized[:-3]
                if normalized.lower().endswith(".py")
                else normalized
            )

            for part in Path(
                path_without_extension
            ).parts:

                part = part.lower().strip()

                if part:
                    path_words.add(
                        part
                    )

        result = set()

        for word in words:

            word = word.strip()

            if not word:
                continue

            if len(word) < 3:
                continue

            if word in ignored:
                continue

            # Do not treat directory/file path components as
            # semantic task concepts.
            if word in path_words:
                continue

            result.add(
                word
            )

        return result