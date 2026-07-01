from utils.time_helper import seconds_to_str, now
from utils.display import (
    separator, title, subtitle, status_icon, crop_emoji,
    format_gold, format_exp, level_bar,
)


class MenuManager:
    def __init__(self, game):
        self.game = game

    def _input_int(self, prompt: str) -> int:
        try:
            return int(input(prompt).strip())
        except (ValueError, EOFError):
            return -1

    def _wait_return(self):
        input("\n按 Enter 返回主菜单...")

    def show_main_menu(self):
        g = self.game
        print(g.get_overview())
        print("1. 查看农场全貌    2. 商店")
        print("3. 播种            4. 收获")
        print("5. 浇水            6. 开垦新地块")
        print("7. 翻地(清理枯萎)  8. 我的背包")
        print("9. 成就与签到      0. 退出游戏")

        choice = self._input_int("请输入数字选择: ")

        if choice == 0:
            g.save_game()
            g.running = False
            print("\n感谢游玩！农场已保存。")
        elif choice == 1:
            self.show_farm_view()
        elif choice == 2:
            self.show_store()
        elif choice == 3:
            self.show_plant_menu()
        elif choice == 4:
            self.show_harvest_menu()
        elif choice == 5:
            self.show_water_menu()
        elif choice == 6:
            self.show_unlock_land()
        elif choice == 7:
            self.show_till_menu()
        elif choice == 8:
            self.show_inventory()
        elif choice == 9:
            self.show_achievements()
        else:
            print("无效输入，请重新选择。")

    def show_farm_view(self):
        g = self.game
        print(g.get_farm_view())
        self._wait_return()

    def show_store(self):
        g = self.game
        level = g.economy.level
        print(title("种子商店"))
        crops = g.store.get_store_list(level)
        if not crops:
            print("暂无可用作物。")
            self._wait_return()
            return
        for i, crop in enumerate(crops, 1):
            print(f"{i}. {crop.name}  {crop.seed_price}💰 ({seconds_to_str(crop.mature_seconds)})  Lv.{crop.level_required}")
        print(f"{separator()}")
        print(f"0. 返回主菜单   9. 装饰商店")
        choice = self._input_int("输入编号选择要买的种子: ")
        if choice == 0:
            return
        if choice == 9:
            self.show_decoration_shop()
            return
        if 1 <= choice <= len(crops):
            crop = crops[choice - 1]
            success, msg = g.store.buy_seed(crop.crop_id)
            print(f">> {msg}")
        else:
            print("无效输入。")
        self._wait_return()

    def show_decoration_shop(self):
        g = self.game
        print(title("装饰商店"))
        items = g.store.get_decoration_list()
        for i, (item_id, name, price) in enumerate(items, 1):
            owned = "✅" if g.inventory.has_decoration(item_id) else ""
            print(f"{i}. {name}  {price}💰  {owned}")
        print(separator())
        print("0. 返回")
        choice = self._input_int("输入编号购买装饰: ")
        if choice == 0:
            return
        if 1 <= choice <= len(items):
            item_id = items[choice - 1][0]
            success, msg = g.store.buy_decoration(item_id)
            print(f">> {msg}")
        else:
            print("无效输入。")
        self._wait_return()

    def show_plant_menu(self):
        g = self.game
        empty_lands = g.land_system.get_lands_by_status("empty")
        if not empty_lands:
            print("没有空地可播种。先去翻地或开垦新地块吧！")
            self._wait_return()
            return
        print("请选择要播种的地块:")
        for land in g.land_system.lands:
            lid = land["id"]
            status = land["status"]
            icon = status_icon(status)
            if status == "growing":
                crop = g.crop_system.get_crop(land["crop_id"])
                name = crop.name if crop else "???"
                print(f"  {lid}. 地块#{lid} [{name} 生长中]")
            elif status == "mature":
                crop = g.crop_system.get_crop(land["crop_id"])
                name = crop.name if crop else "???"
                print(f"  {lid}. 地块#{lid} [{name} 🟢 已成熟]")
            elif status == "withered":
                print(f"  {lid}. 地块#{lid} [💀 枯萎]")
            else:
                print(f"  {lid}. 地块#{lid} [空地] {icon} ←")
        print(separator())
        land_choice = self._input_int("输入地块编号 (0 返回): ")
        if land_choice == 0:
            return
        land = g.land_system.get_land(land_choice)
        if land is None or land["status"] != "empty":
            print("该地块无法播种。")
            self._wait_return()
            return
        level = g.economy.level
        crops = g.crop_system.get_available_crops(level)
        if not g.inventory.seeds:
            print("背包中没有种子，请先去商店购买！")
            self._wait_return()
            return
        print(title("选择种子"))
        seed_list = []
        for crop in crops:
            count = g.inventory.get_seed_count(crop.crop_id)
            if count > 0:
                seed_list.append(crop)
                print(f"  {len(seed_list)}. {crop.name} 库存:{count} | 售价:{crop.sell_price}💰 经验:{crop.exp}")
        if not seed_list:
            print("没有可用的种子，请先去商店购买！")
            self._wait_return()
            return
        print("0. 返回")
        seed_choice = self._input_int("选择种子编号: ")
        if seed_choice == 0:
            return
        if 1 <= seed_choice <= len(seed_list):
            crop = seed_list[seed_choice - 1]
            if not g.inventory.use_seed(crop.crop_id):
                print("种子不足！")
                self._wait_return()
                return
            g.land_system.plant(land_choice, crop.crop_id)
            print(f">> ✅ 在 地块#{land_choice} 播种 {crop.name} 成功！")
            g.save_game()
        else:
            print("无效输入。")
        self._wait_return()

    def show_harvest_menu(self):
        g = self.game
        mature_lands = g.land_system.get_lands_by_status("mature")
        if not mature_lands:
            print("没有可收获的作物。")
            self._wait_return()
            return
        print("可收获的地块:")
        for i, land in enumerate(mature_lands, 1):
            crop = g.crop_system.get_crop(land["crop_id"])
            name = crop.name if crop else "???"
            emoji = crop_emoji(land["crop_id"])
            print(f"  {i}. 地块#{land['id']} [{name}] {emoji}")
        print(separator())
        print("输入编号收获，或 0 返回:")
        choice = self._input_int("选择: ")
        if choice == 0:
            return
        if choice == -1:
            print("无效输入。")
            self._wait_return()
            return
        if 1 <= choice <= len(mature_lands):
            lands_to_harvest = [mature_lands[choice - 1]]
        else:
            print("无效输入。")
            self._wait_return()
            return
        total_gold = 0
        total_exp = 0
        for land in lands_to_harvest:
            result = g.land_system.harvest(land["id"])
            if result:
                crop = g.crop_system.get_crop(result["crop_id"])
                if crop:
                    gold_earned = crop.sell_price * result["count"]
                    exp_earned = crop.exp * result["count"]
                    g.economy.add_gold(gold_earned)
                    g.economy.add_exp(exp_earned)
                    g.achievement.record_harvest(result["crop_id"], gold_earned)
                    total_gold += gold_earned
                    total_exp += exp_earned
                    emoji = crop_emoji(result["crop_id"])
                    print(f">> ✅ 收获 {emoji} {crop.name} +{gold_earned}💰 +{exp_earned}经验")
        new_achievements = g.achievement.check_achievements(g.economy.gold)
        for ach in new_achievements:
            print(f">> 🎉 解锁成就：{ach}！")
        g.save_game()
        self._wait_return()

    def show_water_menu(self):
        g = self.game
        growing_lands = g.land_system.get_lands_by_status("growing")
        if not growing_lands:
            print("没有生长中的作物需要浇水。")
            self._wait_return()
            return
        print("选择要浇水的地块:")
        for i, land in enumerate(growing_lands, 1):
            crop = g.crop_system.get_crop(land["crop_id"])
            if crop:
                rem = g.crop_system.get_mature_remaining(land["crop_id"], land["plant_time"], now())
                reduction = land["water_count"] * 60
                print(f"  {i}. 地块#{land['id']} [{crop.name}] 剩余{seconds_to_str(rem)} | 已减{reduction}s")
        print(separator())
        print("0. 返回")
        choice = self._input_int("输入地块编号 (0 返回): ")
        if choice == 0:
            return
        if 1 <= choice <= len(growing_lands):
            land = growing_lands[choice - 1]
            g.land_system.water(land["id"])
            print(f">> 💧 地块#{land['id']} 浇水成功！生长时间-60秒")
            g.save_game()
        else:
            print("无效输入。")
        self._wait_return()

    def show_unlock_land(self):
        g = self.game
        current = g.land_system.get_total_count()
        cost = current * 200
        new_total = current + 3
        print(title("开垦新地块"))
        print(f"当前地块: {current} 块")
        print(f"开垦 {3} 块新地需要 {cost}💰")
        print(f"开垦后: {new_total} 块")
        print(separator())
        print("1. 确认开垦  2. 取消")
        choice = self._input_int("选择: ")
        if choice == 1:
            if g.economy.spend_gold(cost):
                g.land_system.unlock_lands(3)
                print(f">> ✅ 开垦成功！获得 3 块新地，共 {g.land_system.get_total_count()} 块地")
                g.save_game()
            else:
                print(f">> ❌ 金币不足！需要 {cost}💰")
        self._wait_return()

    def show_till_menu(self):
        g = self.game
        withered_lands = g.land_system.get_lands_by_status("withered")
        if not withered_lands:
            print("没有枯萎的地块需要翻地。")
            self._wait_return()
            return
        print("枯萎的地块:")
        for i, land in enumerate(withered_lands, 1):
            print(f"  {i}. 地块#{land['id']} [枯萎] 翻地花费 10💰")
        print(separator())
        print("0. 返回")
        choice = self._input_int("选择要翻地的地块 (0 返回): ")
        if choice == 0:
            return
        if 1 <= choice <= len(withered_lands):
            land = withered_lands[choice - 1]
            print(f"确认翻地 地块#{land['id']}? 1.确认 2.取消")
            confirm = self._input_int("选择: ")
            if confirm == 1:
                if g.economy.spend_gold(10):
                    g.land_system.till(land["id"])
                    print(f">> ✅ 地块#{land['id']} 翻地成功！-10💰")
                    g.save_game()
                else:
                    print(">> ❌ 金币不足！翻地需要 10💰")
        else:
            print("无效输入。")
        self._wait_return()

    def show_inventory(self):
        g = self.game
        print(title("我的背包"))
        print(subtitle("种子"))
        if g.inventory.seeds:
            for crop_id, count in g.inventory.seeds.items():
                crop = g.crop_system.get_crop(crop_id)
                name = crop.name if crop else crop_id
                print(f"  {crop_emoji(crop_id)} {name} ×{count}")
        else:
            print("  (空)")
        print(subtitle("装饰"))
        dec_text = g.inventory.get_active_decoration_text()
        print(f"  {dec_text}")
        print(subtitle("资源"))
        print(f"  金币: {g.economy.gold}💰")
        print(f"  经验: {g.economy.exp}✨")
        next_exp = g.economy.get_exp_to_next_level()
        bar = level_bar(g.economy.exp, g.economy.get_total_exp_for_level(g.economy.level))
        print(f"  等级: Lv.{g.economy.level} {bar} 距下一级还需 {next_exp} 经验")
        print(f"{separator()}")
        self._wait_return()

    def show_achievements(self):
        g = self.game
        print(title("成就与签到"))
        print(subtitle("每日签到"))
        success, msg, *rest = g.achievement.sign_in()
        if len(rest) > 0:
            bonus = rest[0]
            g.economy.add_gold(bonus)
            print(f">> {msg}")
            g.save_game()
        else:
            print(f">> {msg}")
        print(subtitle("成就列表"))
        achievements = g.achievement.get_achievement_list()
        for desc, done in achievements:
            mark = "✅" if done else "⬜"
            print(f"  {mark} {desc}")
        print(subtitle("统计"))
        print(f"  累计收获: {g.achievement.total_harvests} 次")
        print(f"  种植作物: {len(g.achievement.planted_crops)} 种")
        print(f"{separator()}")
        self._wait_return()
