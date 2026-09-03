from app.core.logger import AppLogger

from tools.base_tool import BaseTool



class Calculator(BaseTool):


    name = "calculator"

    description = (
        "Performs basic mathematical operations "
        "such as addition, subtraction, multiplication and division."
    )

    purpose = (
        "Perform mathematical calculations."
    )

    safe = True

    modifies_files = False

    requires_confirmation = False

    version = "1.0"



    def __init__(self):

        self.logger = AppLogger()





    def execute(
        self,
        plan
    ):

        operation = plan.get(
            "operation"
        )

        numbers = plan.get(
            "numbers",
            []
        )

        if len(numbers) < 2:

            return {
                "success": False,
                "error": "At least two numbers are required for the operation."
            }

        try:

            a = float(
                numbers[0]
            )

            b = float(
                numbers[1]
            )

            if operation == "add":

                result = self.add(
                    a,
                    b
                )

            elif operation == "subtract":

                result = self.subtract(
                    a,
                    b
                )

            elif operation == "multiply":

                result = self.multiply(
                    a,
                    b
                )

            elif operation == "divide":

                result = self.divide(
                    a,
                    b
                )

            else:

                return {
                    "success": False,
                    "error": "Unsupported operation"
                }

            if isinstance(result, str):

                return {
                    "success": False,
                    "error": result
                }

            return {
                "success": True,
                "data": result
            }

        except Exception as error:

            self.logger.error(
                f"Calculator error: {error}"
            )

            return {
                "success": False,
                "error": f"Calculator error: {error}"
            }


    def add(
        self,
        a,
        b
    ):


        return a + b







    def subtract(
        self,
        a,
        b
    ):


        return a - b







    def multiply(
        self,
        a,
        b
    ):


        return a * b







    def divide(
        self,
        a,
        b
    ):


        if b == 0:


            return "Cannot divide by zero."



        return a / b