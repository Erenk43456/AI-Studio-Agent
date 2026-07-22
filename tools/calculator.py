class Calculator:


    def clean_result(self, value):

        if isinstance(value, float):

            if value.is_integer():

                return int(value)

        return value




    def validate_numbers(self, a, b):

        if not isinstance(a, (int, float)):

            return False


        if not isinstance(b, (int, float)):

            return False


        return True




    def add(
        self,
        a,
        b
    ):

        if not self.validate_numbers(a, b):

            return "Invalid numbers."


        return self.clean_result(
            a + b
        )




    def subtract(
        self,
        a,
        b
    ):

        if not self.validate_numbers(a, b):

            return "Invalid numbers."


        return self.clean_result(
            a - b
        )




    def multiply(
        self,
        a,
        b
    ):

        if not self.validate_numbers(a, b):

            return "Invalid numbers."


        return self.clean_result(
            a * b
        )




    def divide(
        self,
        a,
        b
    ):

        if not self.validate_numbers(a, b):

            return "Invalid numbers."


        if b == 0:

            return "Division by zero is not allowed."


        return self.clean_result(
            a / b
        )