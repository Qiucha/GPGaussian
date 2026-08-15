"""Override decoded PhysGaussian time_params without editing the config JSON."""


def apply_frame_num_override(time_params: dict, frame_num: int | None) -> dict:
    if frame_num is None:
        return time_params
    time_params["frame_num"] = int(frame_num)
    return time_params
