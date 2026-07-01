class InventorySystem:
    def __init__(self):
        self.seeds: dict[str, int] = {}
        self.decorations: list[str] = []

    def add_seed(self, crop_id: str, count: int = 1):
        self.seeds[crop_id] = self.seeds.get(crop_id, 0) + count

    def use_seed(self, crop_id: str) -> bool:
        if self.seeds.get(crop_id, 0) <= 0:
            return False
        self.seeds[crop_id] -= 1
        if self.seeds[crop_id] <= 0:
            del self.seeds[crop_id]
        return True

    def get_seed_count(self, crop_id: str) -> int:
        return self.seeds.get(crop_id, 0)

    def add_decoration(self, item_id: str):
        if item_id not in self.decorations:
            self.decorations.append(item_id)

    def has_decoration(self, item_id: str) -> bool:
        return item_id in self.decorations

    def get_active_decoration_text(self) -> str:
        if not self.decorations:
            return "你的农场看起来很朴素。"
        names = {
            "fence": "栅栏",
            "scarecrow": "稻草人",
            "windmill": "风车",
            "flowerbed": "花坛",
        }
        parts = [names.get(d, d) for d in self.decorations]
        return "你的农场里有：" + "、".join(parts)
