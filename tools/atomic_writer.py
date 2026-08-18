import os
import tempfile
from pathlib import Path

from app.core.logger import AppLogger


class AtomicWriter:

    name = "atomic_writer"

    description = (
        "Writes validated file content atomically "
        "within the workspace."
    )

    purpose = (
        "Safely commit validated code changes to the workspace "
        "without exposing partially written files."
    )

    safe = False

    modifies_files = True

    requires_confirmation = False

    version = "1.0"

    def __init__(
        self,
        workspace
    ):

        self.workspace = Path(
            workspace
        ).resolve()

        self.logger = AppLogger()

    def write(
        self,
        path,
        content,
        simulate_failure=False
    ):

        target = Path(
            path
        ).resolve()

        try:

            # -----------------------------------------------------
            # Workspace isolation
            # -----------------------------------------------------

            try:

                target.relative_to(
                    self.workspace
                )

            except ValueError:

                return {
                    "success": False,
                    "error": (
                        "Target path is outside workspace."
                    )
                }

            # -----------------------------------------------------
            # Ensure parent directory exists
            # -----------------------------------------------------

            target.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            # -----------------------------------------------------
            # Write candidate to temporary file
            # -----------------------------------------------------

            fd, temporary_path = tempfile.mkstemp(
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp"
            )

            try:

                with os.fdopen(
                    fd,
                    "w",
                    encoding="utf-8"
                ) as file:

                    file.write(
                        content
                    )

                    file.flush()

                    os.fsync(
                        file.fileno()
                    )

                # -------------------------------------------------
                # Testing hook
                # -------------------------------------------------

                if simulate_failure:

                    raise RuntimeError(
                        "Simulated atomic write failure."
                    )

                # -------------------------------------------------
                # Atomic replacement
                # -------------------------------------------------

                os.replace(
                    temporary_path,
                    target
                )

            finally:

                # If os.replace succeeded the temporary file
                # no longer exists.
                if os.path.exists(
                    temporary_path
                ):

                    os.unlink(
                        temporary_path
                    )

            self.logger.info(
                f"Atomic write completed: {target}"
            )

            return {
                "success": True,
                "path": str(target)
            }

        except Exception as error:

            self.logger.error(
                f"Atomic write failed: {target}: {error}"
            )

            return {
                "success": False,
                "path": str(target),
                "error": str(error)
            }