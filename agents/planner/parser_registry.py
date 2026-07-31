class ParserRegistry:

    def __init__(self):

        self.parsers = []


    def register(self, parser):

        self.parsers.append(parser)

        self.parsers.sort(
            key=lambda p: p.priority
        )


    def parse(self, message):

        for parser in self.parsers:

            plan = parser.parse(message)

            if plan:

                return plan

        return None