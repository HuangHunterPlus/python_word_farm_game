from utils.time_helper import today_str


ACHIEVEMENT_DEFS = {
    "first_harvest": "🌱 初次收获 —— 第一次收获作物",
    "harvest_100": "🏆 丰收达人 —— 累计收获 100 次",
    "all_crops": "📖 植物图鉴 —— 种植过所有作物",
    "gold_10000": "💰 万元户 —— 累计拥有 10000 金币",
}


class AchievementSystem:
    def __init__(self):
        self.achievements: dict[str, bool] = {}
        self.total_harvests: int = 0
        self.planted_crops: set[str] = set()
        self.max_gold: int = 0
        self.sign_in_last: str = ""
        self.sign_in_days: int = 0

    def record_harvest(self, crop_id: str, gold_earned: int):
        self.total_harvests += 1
        self.planted_crops.add(crop_id)

    def sign_in(self) -> tuple[bool, str]:
        today = today_str()
        if self.sign_in_last == today:
            return False, "今天已经签到过了！"
        if self.sign_in_last == "":
            self.sign_in_days = 1
        else:
            from datetime import datetime, timedelta
            try:
                last = datetime.strptime(self.sign_in_last, "%Y-%m-%d")
                expected = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
                if self.sign_in_last == expected:
                    self.sign_in_days += 1
                else:
                    self.sign_in_days = 1
            except ValueError:
                self.sign_in_days = 1
        self.sign_in_last = today
        bonus = 10 + (self.sign_in_days - 1) * 5
        return True, f"签到成功！连续签到 {self.sign_in_days} 天，获得 {bonus}💰", bonus

    def check_achievements(self, economy_gold: int) -> list[str]:
        unlocked = []
        if "first_harvest" not in self.achievements and self.total_harvests >= 1:
            self.achievements["first_harvest"] = True
            unlocked.append("🌱 初次收获")
        if "harvest_100" not in self.achievements and self.total_harvests >= 100:
            self.achievements["harvest_100"] = True
            unlocked.append("🏆 丰收达人")
        if "gold_10000" not in self.achievements and economy_gold >= 10000:
            self.achievements["gold_10000"] = True
            unlocked.append("💰 万元户")
        if "all_crops" not in self.achievements:
            from systems.crop import CropSystem
            all_ids = {"carrot", "potato", "tomato", "strawberry", "wheat",
                       "apple_tree", "orange_tree", "grape", "lingzhi"}
            if all_ids.issubset(self.planted_crops):
                self.achievements["all_crops"] = True
                unlocked.append("📖 植物图鉴")
        return unlocked

    def get_achievement_list(self) -> list[tuple[str, bool]]:
        result = []
        for key, desc in ACHIEVEMENT_DEFS.items():
            done = self.achievements.get(key, False)
            result.append((desc, done))
        return result
