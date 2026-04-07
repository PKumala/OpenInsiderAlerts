class BaseFilter:
    """
    Każdy filtr musi dziedziczyć po tej klasie
    """

    type = "base"

    def __init__(self, params: dict):
        self.params = params or {}

    def check(self, trade) -> bool:
        """
        trade = obiekt AnalyzedTrade
        Zwraca True jeśli trade przechodzi filtr
        """
        raise NotImplementedError