from typing import Optional
from utils.time_helper import now


WITHER_TIMEOUT = 1800


class LandSystem:
    def __init__(self, land_count: int = 6):
        self.lands: list[dict] = []
        self._max_lands = land_count
        self._init_lands(land_count)

    def _init_lands(self, count: int):
        self.lands = []
        for i in range(1, count + 1):
            self.lands.append({
                "id": i,
                "status": "empty",
                "crop_id": None,
                "plant_time": None,
                "water_count": 0,
            })

    def get_land(self, land_id: int) -> Optional[dict]:
        for land in self.lands:
            if land["id"] == land_id:
                return land
        return None

    def get_lands_by_status(self, status: str) -> list[dict]:
        return [l for l in self.lands if l["status"] == status]

    def plant(self, land_id: int, crop_id: str) -> bool:
        land = self.get_land(land_id)
        if land is None or land["status"] != "empty":
            return False
        land["status"] = "growing"
        land["crop_id"] = crop_id
        land["plant_time"] = now()
        land["water_count"] = 0
        return True

    def harvest(self, land_id: int) -> Optional[dict]:
        land = self.get_land(land_id)
        if land is None or land["status"] not in ("mature", "withered"):
            return None
        result = {
            "crop_id": land["crop_id"],
            "count": 1,
        }
        land["status"] = "empty"
        land["crop_id"] = None
        land["plant_time"] = None
        land["water_count"] = 0
        return result

    def water(self, land_id: int) -> bool:
        land = self.get_land(land_id)
        if land is None or land["status"] != "growing":
            return False
        land["water_count"] += 1
        return True

    def till(self, land_id: int) -> bool:
        land = self.get_land(land_id)
        if land is None or land["status"] != "withered":
            return False
        land["status"] = "empty"
        land["crop_id"] = None
        land["plant_time"] = None
        land["water_count"] = 0
        return True

    def unlock_lands(self, count: int) -> bool:
        new_count = len(self.lands) + count
        for i in range(len(self.lands) + 1, new_count + 1):
            self.lands.append({
                "id": i,
                "status": "empty",
                "crop_id": None,
                "plant_time": None,
                "water_count": 0,
            })
        self._max_lands = new_count
        return True

    def get_used_count(self) -> int:
        return len([l for l in self.lands if l["status"] != "empty"])

    def get_total_count(self) -> int:
        return len(self.lands)

    def get_water_reduction(self, land_id: int) -> int:
        return self.get_land(land_id)["water_count"] * 60 if self.get_land(land_id) else 0

    def update_all(self, crop_system, current_time: float):
        for land in self.lands:
            if land["status"] == "growing" and land["plant_time"] is not None:
                crop = crop_system.get_crop(land["crop_id"])
                if crop is None:
                    continue
                reduction = land["water_count"] * 60
                effective_mature = max(crop.mature_seconds - reduction, 10)
                if (current_time - land["plant_time"]) >= effective_mature:
                    land["status"] = "mature"
            elif land["status"] == "mature" and land["plant_time"] is not None:
                crop = crop_system.get_crop(land["crop_id"])
                if crop is None:
                    continue
                reduction = land["water_count"] * 60
                effective_mature = max(crop.mature_seconds - reduction, 10)
                mature_time = land["plant_time"] + effective_mature
                if (current_time - mature_time) >= WITHER_TIMEOUT:
                    land["status"] = "withered"
