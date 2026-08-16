from app.core.logger import AppLogger


class DevelopmentOrchestrator:

    def __init__(
        self,
        container
    ):

        self.container = container

        self.planner = container.planner

        self.code_agent = container.code_agent

        self.repository_analyzer = (
            container.repository_analyzer
        )

        self.improvement_agent = (
            container.improvement_agent
        )

        self.logger = AppLogger()


    def run(
        self,
        message,
        decision=None,
        conversation=None
    ):

        self.logger.info(
            f"Development request: {message}"
        )


        if decision is None:

            decision = {
                "action": "code"
            }


        action = decision.get(
            "action",
            "code"
        )


        #
        # Repository analysis
        #

        if action == "analyze":

            if not self.repository_analyzer:

                return (
                    "❌ Repository analyzer "
                    "kullanılamıyor."
                )


            result = self.repository_analyzer.execute(
                {
                    "action": "analyze"
                }
            )


            return self.format_result(
                result
            )


        #
        # Improvement
        #

        if action == "improve":

            if not self.improvement_agent:

                return (
                    "❌ Improvement agent "
                    "kullanılamıyor."
                )


            result = self.improvement_agent.execute(
                message
            )


            return self.format_result(
                result
            )


        #
        # Normal development task
        #

        return self.execute_code_task(
            message
        )


    def execute_code_task(
        self,
        message
    ):

        #
        # Planner
        #

        plan = self.planner.create_plan(
            message
        )


        if not plan:

            self.logger.error(
                "Planner failed."
            )

            return (
                "❌ İstek için bir plan "
                "oluşturulamadı."
            )


        #
        # Debug
        #

        self.logger.info(
            f"Development plan: {plan}"
        )

        print(
            "PLAN:",
            plan
        )


        #
        # Steps
        #

        steps = plan.get(
            "steps",
            []
        )


        if not steps:

            return (
                "❌ Planner herhangi bir "
                "işlem oluşturmadı."
            )


        #
        # Execute steps
        #

        results = []

        overall_success = True


        for step in steps:

            if not isinstance(
                step,
                dict
            ):

                overall_success = False

                results.append({

                    "success": False,

                    "error":
                        "Invalid planner step."

                })

                continue


            tool_name = step.get(
                "tool"
            )


            if not tool_name:

                self.logger.warning(
                    "Planner step has no tool."
                )

                overall_success = False

                results.append({

                    "success": False,

                    "error":
                        "Planner step has no tool."

                })

                continue


            self.logger.info(
                f"Executing tool: {tool_name}"
            )


            #
            # Code agent
            #

            if tool_name == "code":

                try:

                    result = self.code_agent.run(

                        step.get(
                            "input",
                            message
                        )

                    )


                    results.append(
                        result
                    )


                    if isinstance(
                        result,
                        dict
                    ):

                        if not result.get(
                            "success",
                            False
                        ):

                            overall_success = False


                    continue


                except Exception as error:

                    overall_success = False

                    results.append({

                        "success": False,

                        "tool":
                            "code",

                        "error":
                            str(error)

                    })

                    continue


            #
            # Tool registry
            #

            tool = self.container.registry.get(
                tool_name
            )


            if not tool:

                self.logger.error(
                    f"Tool not found: {tool_name}"
                )

                overall_success = False

                results.append({

                    "success": False,

                    "tool":
                        tool_name,

                    "error":
                        f"Tool not found: {tool_name}"

                })

                continue


            #
            # Execute tool
            #

            try:

                result = tool.execute(
                    step
                )


                results.append(
                    result
                )


                #
                # Detect tool failure
                #

                if isinstance(
                    result,
                    dict
                ):

                    if not result.get(
                        "success",
                        False
                    ):

                        overall_success = False


                elif isinstance(
                    result,
                    str
                ):

                    if result.startswith(
                        "Tool error:"
                    ):

                        overall_success = False


            except Exception as error:

                self.logger.error(

                    f"Tool execution failed: "
                    f"{tool_name}: {error}"

                )


                overall_success = False


                results.append({

                    "success": False,

                    "tool":
                        tool_name,

                    "error":
                        str(error)

                })


        #
        # Human-readable response
        #

        return self.format_results(
            results,
            overall_success
        )


    def format_results(
        self,
        results,
        overall_success
    ):

        if not results:

            return (
                "❌ Herhangi bir işlem "
                "gerçekleştirilemedi."
            )


        messages = []


        for result in results:

            messages.append(
                self.format_result(
                    result
                )
            )


        if overall_success:

            return "\n\n".join(
                messages
            )


        return "\n\n".join(
            messages
        )


    def format_result(
        self,
        result
    ):

        if result is None:

            return (
                "❌ İşlem sonucunda "
                "herhangi bir sonuç alınamadı."
            )


        if isinstance(
            result,
            str
        ):

            return result


        if not isinstance(
            result,
            dict
        ):

            return str(
                result
            )


        success = result.get(
            "success",
            False
        )


        action = result.get(
            "action",
            ""
        )


        #
        # File tool
        #

        if action == "write":

            if success:

                filename = result.get(
                    "file",
                    result.get(
                        "filename",
                        "dosya"
                    )
                )

                return (
                    f"✅ Dosya başarıyla yazıldı.\n\n"
                    f"📄 {filename}"
                )


            error = result.get(
                "error",
                result.get(
                    "message",
                    "Bilinmeyen hata."
                )
            )

            return (
                f"❌ Dosya yazılamadı.\n\n"
                f"Sebep: {error}"
            )


        if action == "create":

            if success:

                filename = result.get(
                    "file",
                    result.get(
                        "filename",
                        "dosya"
                    )
                )

                return (
                    f"✅ Dosya başarıyla oluşturuldu.\n\n"
                    f"📄 {filename}"
                )


            error = result.get(
                "error",
                result.get(
                    "message",
                    "Bilinmeyen hata."
                )
            )

            return (
                f"❌ Dosya oluşturulamadı.\n\n"
                f"Sebep: {error}"
            )


        if action == "read":

            if success:

                filename = result.get(
                    "file",
                    result.get(
                        "filename",
                        "dosya"
                    )
                )


                content = result.get(
                    "content",
                    ""
                )


                return (
                    f"📄 {filename}\n\n"
                    f"İçerik:\n"
                    f"{content}"
                )


            error = result.get(
                "error",
                result.get(
                    "message",
                    "Bilinmeyen hata."
                )
            )


            return (
                f"❌ Dosya okunamadı.\n\n"
                f"Sebep: {error}"
            )


        #
        # Code analyzer
        #

        if "analysis" in result:

            analysis = result.get(
                "analysis"
            )

            filename = result.get(
                "file",
                result.get(
                    "filename",
                    "dosya"
                )
            )


            if not isinstance(
                analysis,
                dict
            ):

                return (
                    f"📄 {filename}\n\n"
                    f"Analiz sonucu:\n"
                    f"{analysis}"
                )


            lines = [

                f"📄 {filename}",

                ""

            ]


            summary = analysis.get(
                "summary"
            )


            if summary:

                lines.extend([

                    "📋 Özet:",

                    str(summary),

                    ""

                ])


            sections = [

                (
                    "syntax_errors",
                    "Syntax hataları"
                ),

                (
                    "logical_errors",
                    "Mantıksal hatalar"
                ),

                (
                    "security_issues",
                    "Güvenlik sorunları"
                ),

                (
                    "performance_issues",
                    "Performans sorunları"
                ),

                (
                    "architecture_issues",
                    "Mimari sorunlar"
                ),

                (
                    "improvements",
                    "İyileştirmeler"
                )

            ]


            for key, title in sections:

                values = analysis.get(
                    key,
                    []
                )


                if not values:

                    continue


                lines.append(
                    f"🔹 {title}:"
                )


                if isinstance(
                    values,
                    list
                ):

                    for value in values:

                        lines.append(
                            f"- {value}"
                        )

                else:

                    lines.append(
                        f"- {values}"
                    )


                lines.append("")


            risk_level = analysis.get(
                "risk_level"
            )


            if risk_level:

                lines.append(
                    f"⚠️ Risk seviyesi: "
                    f"{risk_level}"
                )


            return "\n".join(
                lines
            )


        #
        # Generic success
        #

        if success:

            message = result.get(
                "message"
            )


            if message:

                return (
                    f"✅ {message}"
                )


            return (
                "✅ İşlem başarıyla tamamlandı."
            )


        #
        # Generic error
        #

        error = result.get(
            "error",
            result.get(
                "message",
                "Bilinmeyen hata."
            )
        )


        return (
            f"❌ İşlem başarısız.\n\n"
            f"Sebep: {error}"
        )