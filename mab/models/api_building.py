class MeterDeviceAPI:

    def __init__(self, model):
        self.model_api = model
        self.pk_device = model.pk
        self.date = None
        self.current_values = 0
        self.previous_values = 0

