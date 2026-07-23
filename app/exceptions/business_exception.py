class BusinessException(Exception):

    def __init__(self, validation_rule):
        self.validation_rule = validation_rule
        super().__init__(validation_rule.message)