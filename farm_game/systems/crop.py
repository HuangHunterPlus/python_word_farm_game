import json
from dataclasses import dataclass
from typing import Optional


@dataclass
class CropData:
    crop_id: str
    name: str
    seed_price: int
    mature_seconds: int
    sell_price: int
    exp: int
    level_required: int


class CropSystem:
    def __init__(self):
        self._crops: dict[str, CropData] = {}

    def load_from_json(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            raw_list = json.load(f)
        for item in raw_list:
            crop = CropData(**item)
            self._crops[crop.crop_id] = crop

    def get_crop(self, crop_id: str) -> Optional[CropData]:
        return self._crops.get(crop_id)

    def get_available_crops(self, level: int) -> list[CropData]:
        return [c for c in self._crops.values() if level >= c.level_required]

    def get_all_crops(self) -> list[CropData]:
        return list(self._crops.values())

    def get_mature_remaining(self, crop_id: str, plant_time: float, now_time: float) -> int:
        crop = self.get_crop(crop_id)
        if crop is None:
            return 0
        elapsed = now_time - plant_time
        remaining = crop.mature_seconds - elapsed
        return max(0, int(remaining))

    def is_mature(self, crop_id: str, plant_time: float, now_time: float) -> bool:
        crop = self.get_crop(crop_id)
        if crop is None:
            return False
        return (now_time - plant_time) >= crop.mature_seconds
