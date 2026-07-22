class Calculator:


    def clean_result(self, value):

        if isinstance(value, float):

            if value.is_integer():
                return int(value)

        return value



    def add(
        self,
        a,
        b
    ):

        return self.clean_result(
            a + b
        )



    def subtract(
        self,
        a,
        b
    ):

        return self.clean_result(
            a - b
        )



    def multiply(
        self,
        a,
        b
    ):

        return self.clean_result(
            a * b
        )



    def divide(
        self,
        a,
        b
    ):

        if b == 0:
            return "Division by zero is not allowed."


        return self.clean_result(
            a / b
        )