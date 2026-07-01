import json
import os
import sys

from systems.crop import CropSystem
from systems.land import LandSystem
from systems.economy import EconomySystem
from systems.inventory import InventorySystem
from systems.store import StoreSystem
from systems.achievement import AchievementSystem
from utils.time_helper import now, seconds_to_str
from utils.display import status_icon, crop_emoji


SAVE_DIR = os.path.join(os.path.dirname(__file__), "save")
CROPS_DATA = os.path.join(os.path.dirname(__file__), "data", "crops.json")


class Game:
    def __init__(self):
        self.crop_system = CropSystem()
        self.crop_system.load_from_json(CROPS_DATA)
        self.land_system = LandSystem(6)
        self.economy = EconomySystem(100, 0)
        self.inventory = InventorySystem()
        self.achievement = AchievementSystem()
        self.store = StoreSystem(self.crop_system, self.economy, self.inventory)
        self.running = True
        self._load_or_new()

    def _load_or_new(self):
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR, exist_ok=True)
        saves = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
        if saves:
            self.load_game(os.path.join(SAVE_DIR, saves[0]))
        else:
            self.new_game()

    def new_game(self):
        self.land_system = LandSystem(6)
        self.economy = EconomySystem(100, 0)
        self.inventory = InventorySystem()
        self.achievement = AchievementSystem()
        self.store = StoreSystem(self.crop_system, self.economy, self.inventory)

    def load_game(self, filepath: str):
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        pd = data.get("player", {})
        self.economy = EconomySystem(pd.get("gold", 100), pd.get("exp", 0))
        self.land_system = LandSystem(0)
        self.land_system.lands = data.get("lands", [])
        inv = data.get("inventory", {})
        self.inventory = InventorySystem()
        self.inventory.seeds = inv.get("seeds", {})
        self.inventory.decorations = inv.get("decorations", [])
        ad = data.get("achievements", {})
        self.achievement = AchievementSystem()
        self.achievement.achievements = ad.get("achievements", {})
        self.achievement.total_harvests = ad.get("total_harvests", 0)
        self.achievement.planted_crops = set(ad.get("planted_crops", []))
        self.achievement.sign_in_last = ad.get("sign_in_last", "")
        self.achievement.sign_in_days = ad.get("sign_in_days", 0)
        self.store = StoreSystem(self.crop_system, self.economy, self.inventory)

    def save_game(self):
        os.makedirs(SAVE_DIR, exist_ok=True)
        filepath = os.path.join(SAVE_DIR, "save_001.json")
        data = {
            "version": 1,
            "player": {
                "gold": self.economy.gold,
                "exp": self.economy.exp,
            },
            "lands": self.land_system.lands,
            "inventory": {
                "seeds": self.inventory.seeds,
                "decorations": self.inventory.decorations,
            },
            "achievements": {
                "achievements": self.achievement.achievements,
                "total_harvests": self.achievement.total_harvests,
                "planted_crops": list(self.achievement.planted_crops),
                "sign_in_last": self.achievement.sign_in_last,
                "sign_in_days": self.achievement.sign_in_days,
            },
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def tick(self):
        self.land_system.update_all(self.crop_system, now())

    def get_overview(self) -> str:
        level = self.economy.level
        gold = self.economy.gold
        used = self.land_system.get_used_count()
        total = self.land_system.get_total_count()
        lines = []
        lines.append("")
        lines.append(f"{'='*12} 【开心农场】 Lv.{level} {'='*12}")
        lines.append(f"🌾 农场概况：金币 {gold}💰 | 地块 {used}/{total}")
        mature_lands = self.land_system.get_lands_by_status("mature")
        if mature_lands:
            hints = [f"地块#{l['id']}(成熟)" for l in mature_lands]
            lines.append(f"⏳ 可收获: {' '.join(hints)}")
        growing_lands = self.land_system.get_lands_by_status("growing")
        if growing_lands:
            parts = []
            for l in growing_lands[:3]:
                crop = self.crop_system.get_crop(l["crop_id"])
                if crop:
                    rem = self.crop_system.get_mature_remaining(l["crop_id"], l["plant_time"], now())
                    parts.append(f"{crop.name} {seconds_to_str(rem)}")
            if parts:
                lines.append(f"📅 快速倒计时: {' | '.join(parts)}")
        lines.append("=" * 40)
        return "\n".join(lines)

    def get_farm_view(self) -> str:
        lines = []
        lines.append(f"{'─'*6} 我的农场 {'─'*6}")
        for land in self.land_system.lands:
            lid = land["id"]
            status = land["status"]
            icon = status_icon(status)
            if status == "empty":
                lines.append(f"  地块#{lid} [空地] {icon} 可播种")
            elif status == "growing":
                crop = self.crop_system.get_crop(land["crop_id"])
                if crop:
                    rem = self.crop_system.get_mature_remaining(land["crop_id"], land["plant_time"], now())
                    lines.append(f"  地块#{lid} [{crop.name}] 生长中 {icon} {seconds_to_str(rem)}")
            elif status == "mature":
                crop = self.crop_system.get_crop(land["crop_id"])
                name = crop.name if crop else "???"
                emoji = crop_emoji(land["crop_id"])
                lines.append(f"  地块#{lid} [{name}] {icon} 已成熟！速收获 {emoji}")
            elif status == "withered":
                lines.append(f"  地块#{lid} [枯萎] {icon} 需要翻地")
        lines.append(f"{'─'*20}")
        return "\n".join(lines)
