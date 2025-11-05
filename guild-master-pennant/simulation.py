"""
Simulation - バランスシミュレーション

ゲームバランスをテストするためのシミュレーション機能。
"""

import random
from typing import List, Dict, Any


class MockAdventurer:
    """
    シミュレーション用の冒険者クラス
    """
    def __init__(self, name: str, job_class: str):
        self.adventurer_name = name
        self.job_class = job_class
        self.formation_position = 0
        self.is_alive = True

        # 職業別ステータス
        self._apply_job_stats()

    def _apply_job_stats(self):
        """職業別ステータスを適用"""
        job_stats = {
            "Warrior": {"max_hp": 100, "attack": 15, "defense": 12, "magic": 3, "speed": 8},
            "Mage": {"max_hp": 60, "attack": 5, "defense": 5, "magic": 20, "speed": 10},
            "Priest": {"max_hp": 70, "attack": 7, "defense": 8, "magic": 15, "speed": 9},
            "Thief": {"max_hp": 75, "attack": 12, "defense": 7, "magic": 5, "speed": 18},
            "Archer": {"max_hp": 80, "attack": 13, "defense": 8, "magic": 6, "speed": 12}
        }

        stats = job_stats.get(self.job_class, job_stats["Warrior"])
        self.max_hp = stats["max_hp"]
        self.current_hp = stats["max_hp"]
        self.attack = stats["attack"]
        self.defense = stats["defense"]
        self.magic = stats["magic"]
        self.speed = stats["speed"]

    def is_in_front_row(self) -> bool:
        """前列にいるか"""
        return self.formation_position < 3

    def get_effective_attack(self) -> int:
        """実効攻撃力"""
        modifier = 1.1 if self.is_in_front_row() else 1.0
        return int(self.attack * modifier)

    def get_effective_defense(self) -> int:
        """実効防御力"""
        modifier = 1.0 if self.is_in_front_row() else 1.1
        return int(self.defense * modifier)

    def get_hit_rate(self) -> float:
        """被弾率"""
        if self.is_in_front_row():
            return 0.6 / 3.0  # 前列3人で60%を分担
        else:
            return 0.1  # 後列は10%

    def take_damage(self, damage: int) -> int:
        """ダメージを受ける"""
        actual_damage = max(1, damage - self.get_effective_defense())
        self.current_hp -= actual_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

        return actual_damage

    def heal(self, amount: int) -> int:
        """回復する"""
        if not self.is_alive:
            return 0

        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old_hp


class MockEnemy:
    """
    シミュレーション用の敵クラス
    """
    def __init__(self, enemy_type: str, scaling: float = 1.0):
        self.name = enemy_type
        self.type = enemy_type
        self.is_alive = True

        # 敵のベースステータス
        enemy_stats = {
            "Goblin": {"hp": 50, "attack": 10, "defense": 5, "magic": 0, "speed": 12},
            "Orc": {"hp": 80, "attack": 15, "defense": 10, "magic": 0, "speed": 6},
            "Dark Mage": {"hp": 40, "attack": 5, "defense": 3, "magic": 18, "speed": 10},
            "Skeleton": {"hp": 60, "attack": 12, "defense": 8, "magic": 0, "speed": 8},
            "Dragon": {"hp": 200, "attack": 25, "defense": 20, "magic": 15, "speed": 14}
        }

        stats = enemy_stats.get(enemy_type, enemy_stats["Goblin"])
        self.max_hp = int(stats["hp"] * scaling)
        self.current_hp = int(stats["hp"] * scaling)
        self.attack = int(stats["attack"] * scaling)
        self.defense = int(stats["defense"] * scaling)
        self.magic = int(stats["magic"] * scaling)
        self.speed = int(stats["speed"] * scaling)

    def take_damage(self, damage: int) -> int:
        """ダメージを受ける"""
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage

        if self.current_hp <= 0:
            self.current_hp = 0
            self.is_alive = False

        return actual_damage


class CombatSimulator:
    """
    戦闘シミュレーター
    """

    @staticmethod
    def calculate_damage(attacker, defender) -> int:
        """ダメージ計算"""
        base_damage = attacker.get_effective_attack() if hasattr(attacker, 'get_effective_attack') else attacker.attack
        defense = defender.get_effective_defense() if hasattr(defender, 'get_effective_defense') else defender.defense

        damage = base_damage - (defense / 2)
        damage = int(damage * random.uniform(0.9, 1.1))

        return max(1, damage)

    @staticmethod
    def select_target_by_hit_rate(targets: List) -> Any:
        """被弾率に基づいてターゲットを選択"""
        total_weight = 0.0
        weights = []

        for target in targets:
            hit_rate = target.get_hit_rate() if hasattr(target, 'get_hit_rate') else 1.0 / len(targets)
            weights.append(hit_rate)
            total_weight += hit_rate

        rand = random.random() * total_weight
        cumulative = 0.0

        for i in range(len(targets)):
            cumulative += weights[i]
            if rand <= cumulative:
                return targets[i]

        return targets[0]

    @staticmethod
    def simulate_turn(party: List, enemies: List) -> Dict:
        """1ターンをシミュレート"""
        # 行動順を決定（速度順）
        all_units = [(u, "party") for u in party if u.is_alive] + [(u, "enemy") for u in enemies if u.is_alive]
        all_units.sort(key=lambda x: x[0].speed, reverse=True)

        turn_log = []

        for unit, side in all_units:
            if not unit.is_alive:
                continue

            # ターゲット選択
            if side == "party":
                alive_enemies = [e for e in enemies if e.is_alive]
                if not alive_enemies:
                    break
                target = alive_enemies[0]  # 最初の敵を攻撃
            else:
                alive_party = [p for p in party if p.is_alive]
                if not alive_party:
                    break
                target = CombatSimulator.select_target_by_hit_rate(alive_party)

            # 攻撃
            damage = CombatSimulator.calculate_damage(unit, target)
            actual_damage = target.take_damage(damage)

            turn_log.append({
                "attacker": unit.adventurer_name if hasattr(unit, 'adventurer_name') else unit.name,
                "target": target.adventurer_name if hasattr(target, 'adventurer_name') else target.name,
                "damage": actual_damage,
                "target_alive": target.is_alive
            })

        return {
            "log": turn_log,
            "party_alive": sum(1 for p in party if p.is_alive),
            "enemies_alive": sum(1 for e in enemies if e.is_alive)
        }

    @staticmethod
    def simulate_combat(party: List, enemies: List, max_turns: int = 100) -> Dict:
        """戦闘全体をシミュレート"""
        turn = 0
        combat_log = []

        while turn < max_turns:
            turn += 1

            party_alive = [p for p in party if p.is_alive]
            enemies_alive = [e for e in enemies if e.is_alive]

            # 勝敗判定
            if not party_alive:
                return {"victory": False, "turns": turn, "log": combat_log}
            if not enemies_alive:
                return {"victory": True, "turns": turn, "log": combat_log}

            # ターン実行
            turn_result = CombatSimulator.simulate_turn(party, enemies)
            combat_log.append(turn_result)

        return {"victory": None, "turns": turn, "log": combat_log}


def simulate_dungeon(party_composition: List[str], max_floors: int = 50) -> Dict:
    """
    ダンジョン踏破をシミュレート

    Args:
        party_composition: パーティ構成（職業名のリスト）
        max_floors: 最大階層数

    Returns:
        シミュレーション結果
    """
    # パーティを作成
    party = []
    for i, job_class in enumerate(party_composition):
        adventurer = MockAdventurer(f"{job_class}{i+1}", job_class)
        adventurer.formation_position = i
        party.append(adventurer)

    floor = 1
    total_victories = 0

    while floor <= max_floors:
        # 敵を生成
        scaling = 1.1 ** (floor - 1)

        if floor <= 3:
            enemies = [MockEnemy("Goblin", scaling) for _ in range(2)]
        elif floor <= 7:
            enemies = [MockEnemy("Goblin", scaling), MockEnemy("Orc", scaling), MockEnemy("Skeleton", scaling)]
        elif floor <= 15:
            enemies = [MockEnemy("Orc", scaling), MockEnemy("Dark Mage", scaling), MockEnemy("Skeleton", scaling)]
        else:
            enemies = [MockEnemy("Dragon", scaling), MockEnemy("Dark Mage", scaling), MockEnemy("Orc", scaling)]

        # 戦闘シミュレート
        result = CombatSimulator.simulate_combat(party, enemies)

        if result["victory"]:
            total_victories += 1
            floor += 1
        else:
            # 全滅
            break

    return {
        "party_composition": party_composition,
        "max_floor_reached": floor - 1,
        "total_victories": total_victories,
        "final_scaling": 1.1 ** (floor - 2) if floor > 1 else 1.0
    }


def run_balance_tests():
    """
    バランステストを実行
    """
    print("\n" + "="*60)
    print("Guild Master Pennant - Balance Simulation")
    print("="*60 + "\n")

    # さまざまなパーティ構成をテスト
    test_compositions = [
        ["Warrior", "Warrior", "Warrior", "Priest"],
        ["Warrior", "Mage", "Priest", "Archer"],
        ["Warrior", "Thief", "Priest", "Mage"],
        ["Thief", "Thief", "Thief", "Priest"],
        ["Archer", "Archer", "Archer", "Priest"]
    ]

    results = []

    for composition in test_compositions:
        print(f"Testing: {', '.join(composition)}")
        result = simulate_dungeon(composition, max_floors=30)
        results.append(result)
        print(f"  Max Floor: {result['max_floor_reached']}")
        print(f"  Final Scaling: {result['final_scaling']:.2f}x\n")

    # 結果をランキング
    results.sort(key=lambda x: x["max_floor_reached"], reverse=True)

    print("\n" + "="*60)
    print("RESULTS - Party Composition Ranking")
    print("="*60 + "\n")

    for i, result in enumerate(results, 1):
        print(f"{i}. {', '.join(result['party_composition'])}")
        print(f"   Max Floor: {result['max_floor_reached']}")
        print(f"   Final Scaling: {result['final_scaling']:.2f}x\n")


if __name__ == "__main__":
    run_balance_tests()
