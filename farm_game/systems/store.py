from systems.crop import CropSystem
from systems.economy import EconomySystem
from systems.inventory import InventorySystem


DECORATIONS = {
    "fence": {"name": "栅栏", "price": 80},
    "scarecrow": {"name": "稻草人", "price": 150},
    "windmill": {"name": "风车", "price": 500},
    "flowerbed": {"name": "花坛", "price": 300},
}


class StoreSystem:
    def __init__(self, crop_system: CropSystem, economy: EconomySystem, inventory: InventorySystem):
        self.crop_system = crop_system
        self.economy = economy
        self.inventory = inventory

    def buy_seed(self, crop_id: str) -> tuple[bool, str]:
        crop = self.crop_system.get_crop(crop_id)
        if crop is None:
            return False, "作物不存在。"
        if self.economy.level < crop.level_required:
            return False, f"等级不足，需要 Lv.{crop.level_required}。"
        if not self.economy.spend_gold(crop.seed_price):
            return False, f"金币不足！需要 {crop.seed_price}💰。"
        self.inventory.add_seed(crop_id)
        return True, f"购买成功！获得 {crop.name} 种子 ×1（-{crop.seed_price}💰）"

    def buy_decoration(self, item_id: str) -> tuple[bool, str]:
        if item_id not in DECORATIONS:
            return False, "装饰不存在。"
        item = DECORATIONS[item_id]
        if not self.economy.spend_gold(item["price"]):
            return False, f"金币不足！需要 {item['price']}💰。"
        self.inventory.add_decoration(item_id)
        return True, f"购买成功！获得 {item['name']}（-{item['price']}💰）"

    def get_store_list(self, level: int) -> list:
        return self.crop_system.get_available_crops(level)

    def get_decoration_list(self) -> list[tuple[str, str, int]]:
        return [(k, v["name"], v["price"]) for k, v in DECORATIONS.items()]
