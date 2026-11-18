class LifeCycleComponent:
    name = "lifecycle"

    def __init__(self, lifecycle, stage_id, time_in_stage):
        self.lifecycle = lifecycle
        self.stage_id = stage_id
        self.time_in_stage = time_in_stage
