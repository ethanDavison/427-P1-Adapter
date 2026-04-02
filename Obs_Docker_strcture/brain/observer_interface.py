# The base interface that all observers must implement
# This is what allows the Brain to notify any observer without knowing what it is
# To add a new observer (e.g. DB Logger), just inherit from this class and implement update()
class ObserverInterface:
    def update(self, data: dict):
        pass