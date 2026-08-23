from app.core.logger import AppLogger


class DevelopmentOrchestrator:

    def __init__(self, container):

        self.container = container

        self.planner = container.planner

        self.tool_agent = container.tool_agent

        self.repository_analyzer = container.repository_analyzer

        self.development_context = container.development_context

        self.project_memory_sync = container.project_memory_sync

        self.improvement_agent = container.improvement_agent

        self.logger = AppLogger()

    def run(self, message, decision=None, conversation=None, execution=None):

        self.logger.info(f"Development request: {message}")

        if decision is None:

            decision = {"action": "code"}

        action = decision.get("action", "code")

        #
        # Execution
        #

        if execution is None:

            execution = {
                "agents": {},
                "models": {},
            }

        #
        # Repository analysis
        #

        if action == "analyze":

            if not self.repository_analyzer:

                return "❌ Repository analyzer " "kullanılamıyor."

            result = self.repository_analyzer.execute({"action": "analyze"})

            return self.format_result(result)

        #
        # Improvement
        #

        if action == "improve":

            if not self.improvement_agent:

                return "❌ Improvement agent " "kullanılamıyor."

            result = self.improvement_agent.execute(message)

            return self.format_result(result)

        #
        # Normal development task
        #

        return self.execute_code_task(message, execution)

    def execute_code_task(self, message, execution=None):

        if execution is None:

            execution = {
                "agents": {},
                "models": {},
            }

        development_context = self.development_context.build(message)

        if (
            development_context["strategy"].get("repository_analysis_fallback", False)
            and self.project_memory_sync
        ):

            self.logger.info(
                "Development context memory is unavailable. "
                "Running repository analysis fallback."
            )

            self.project_memory_sync.sync(development_context["targets"])

            development_context = self.development_context.build(message)

        #
        # Planner
        #

        planner_model = self.planner.llm.get_current_model()

        execution["models"]["planner"] = planner_model

        try:

            plan = self.planner.create_plan(message)

        except Exception as error:

            execution["agents"]["planner"] = {
                "status": "FAIL",
                "model": planner_model,
                "error": str(error),
            }

            self.logger.error(f"Planner failed: {error}")

            return "❌ İstek için bir plan " "oluşturulamadı."

        if not plan:

            execution["agents"]["planner"] = {
                "status": "FAIL",
                "model": planner_model,
                "error": "Planner returned no plan.",
            }

            self.logger.error("Planner failed.")

            return "❌ İstek için bir plan " "oluşturulamadı."

        execution["agents"]["planner"] = {
            "status": "PASS",
            "model": planner_model,
            "result": plan,
        }

        #
        # Debug
        #

        self.logger.info(f"Development plan: {plan}")

        #
        # Steps
        #

        steps = plan.get("steps", [])

        if not steps:

            execution["agents"]["planner"]["status"] = "FAIL"

            execution["agents"]["planner"]["error"] = "Planner returned no steps."

            return "❌ Planner herhangi bir " "işlem oluşturmadı."

        #
        # Execute steps through the canonical execution agent
        #

        code_model = self.container.code_llm.get_current_model()

        execution["models"]["code"] = code_model

        execution_steps = self.tool_agent.execute_steps(
            plan,
            development_context=development_context,
        )

        if isinstance(execution_steps, list):

            results = [
                item.get("result", item) if isinstance(item, dict) else item
                for item in execution_steps
            ]

        else:

            results = [execution_steps]

        overall_success = all(
            not (isinstance(result, dict) and not result.get("success", False))
            and not (isinstance(result, str) and result.startswith("Tool error:"))
            for result in results
        )

        code_results = (
            [
                item
                for item in execution_steps
                if isinstance(item, dict) and item.get("tool") == "code"
            ]
            if isinstance(execution_steps, list)
            else []
        )

        if code_results:

            code_result = code_results[-1].get("result")
            code_success = isinstance(code_result, dict) and code_result.get(
                "success", False
            )

            execution["agents"]["code"] = {
                "status": "PASS" if code_success else "FAIL",
                "model": code_model,
                "result": code_result,
            }

        else:

            execution["agents"]["code"] = {
                "status": "NOT_EVALUATED",
                "model": code_model,
                "reason": "Planner did not execute the code agent.",
            }

        #
        # Human-readable response
        #

        return self.format_results(results, overall_success)

    def format_results(self, results, overall_success):

        if not results:

            return "❌ Herhangi bir işlem " "gerçekleştirilemedi."

        messages = []

        for result in results:

            messages.append(self.format_result(result))

        return "\n\n".join(messages)

    def format_result(self, result):

        if result is None:

            return "❌ İşlem sonucunda " "herhangi bir sonuç alınamadı."

        if isinstance(result, str):

            return result

        if not isinstance(result, dict):

            return str(result)

        success = result.get("success", False)

        action = result.get("action", "")

        #
        # File tool
        #

        if action == "write":

            if success:

                filename = result.get("file", result.get("filename", "dosya"))

                return f"✅ Dosya başarıyla yazıldı.\n\n" f"📄 {filename}"

            error = result.get("error", result.get("message", "Bilinmeyen hata."))

            return f"❌ Dosya yazılamadı.\n\n" f"Sebep: {error}"

        if action == "create":

            if success:

                filename = result.get("file", result.get("filename", "dosya"))

                return f"✅ Dosya başarıyla oluşturuldu.\n\n" f"📄 {filename}"

            error = result.get("error", result.get("message", "Bilinmeyen hata."))

            return f"❌ Dosya oluşturulamadı.\n\n" f"Sebep: {error}"

        if action == "read":

            if success:

                filename = result.get("file", result.get("filename", "dosya"))

                content = result.get("content", "")

                return f"📄 {filename}\n\n" f"İçerik:\n" f"{content}"

            error = result.get("error", result.get("message", "Bilinmeyen hata."))

            return f"❌ Dosya okunamadı.\n\n" f"Sebep: {error}"

        #
        # Code analyzer
        #

        if "analysis" in result:

            analysis = result.get("analysis")

            filename = result.get("file", result.get("filename", "dosya"))

            if not isinstance(analysis, dict):

                return f"📄 {filename}\n\n" f"Analiz sonucu:\n" f"{analysis}"

            lines = [f"📄 {filename}", ""]

            summary = analysis.get("summary")

            if summary:

                lines.extend(["📋 Özet:", str(summary), ""])

            sections = [
                ("syntax_errors", "Syntax hataları"),
                ("logical_errors", "Mantıksal hatalar"),
                ("security_issues", "Güvenlik sorunları"),
                ("performance_issues", "Performans sorunları"),
                ("architecture_issues", "Mimari sorunlar"),
                ("improvements", "İyileştirmeler"),
            ]

            for key, title in sections:

                values = analysis.get(key, [])

                if not values:

                    continue

                lines.append(f"🔹 {title}:")

                if isinstance(values, list):

                    for value in values:

                        lines.append(f"- {value}")

                else:

                    lines.append(f"- {values}")

                lines.append("")

            risk_level = analysis.get("risk_level")

            if risk_level:

                lines.append(f"⚠️ Risk seviyesi: " f"{risk_level}")

            return "\n".join(lines)

        #
        # Code agent
        #

        if "write_result" in result:

            write_result = result.get("write_result")

            if isinstance(write_result, dict):

                if write_result.get("success", False):

                    return "✅ Kod başarıyla güncellendi."

                results = write_result.get("results", [])

                errors = []

                for item in results:

                    if not isinstance(item, dict):

                        continue

                    error = item.get("error")

                    if error:

                        filename = item.get("file", "dosya")

                        errors.append(f"📄 {filename}: {error}")

                if errors:

                    return "❌ Kod güncellenemedi.\n\n" + "\n".join(errors)

            error = result.get("error")

            if error:

                return f"❌ Kod işlemi başarısız.\n\n" f"Sebep: {error}"

            return "❌ Kod işlemi başarısız.\n\n" "Code Agent işlemi tamamlayamadı."

        #
        # Generic success
        #

        if success:

            message = result.get("message")

            if message:

                return f"✅ {message}"

            return "✅ İşlem başarıyla tamamlandı."

        #
        # Generic error
        #

        error = result.get("error", result.get("message", "Bilinmeyen hata."))

        return f"❌ İşlem başarısız.\n\n" f"Sebep: {error}"
