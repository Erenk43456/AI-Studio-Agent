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


            return "Two numbers required."





        try:


            a = float(
                numbers[0]
            )


            b = float(
                numbers[1]
            )





            if operation == "add":

                return self.add(
                    a,
                    b
                )



            if operation == "subtract":

                return self.subtract(
                    a,
                    b
                )



            if operation == "multiply":

                return self.multiply(
                    a,
                    b
                )



            if operation == "divide":

                return self.divide(
                    a,
                    b
                )





            return "Unsupported operation."





        except Exception as error:


            self.logger.error(

                f"Calculator error: {error}"

            )


            return f"Calculator error: {error}"









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