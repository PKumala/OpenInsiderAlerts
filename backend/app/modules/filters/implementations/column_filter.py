from app.modules.filters.base import BaseFilter


class ColumnFilter(BaseFilter):
    type = "column"

    def check(self, trade):

        field = self.params.get("field")
        operator = self.params.get("operator")
        value = self.params.get("value")

        if not hasattr(trade, field):
            return False

        trade_value = getattr(trade, field)

        if trade_value is None:
            return False

        # normalizacja
        if isinstance(trade_value, str):
            trade_value = trade_value.upper()

        if isinstance(value, str):
            value = value.upper()

        if operator == ">":
            return trade_value > value

        if operator == "<":
            return trade_value < value

        if operator == ">=":
            return trade_value >= value

        if operator == "<=":
            return trade_value <= value

        if operator == "==":
            return trade_value == value

        if operator == "!=":
            return trade_value != value

        if operator == "in":
            if not isinstance(value, list):
                return False
            return trade_value in [str(v).upper() for v in value]

        return False