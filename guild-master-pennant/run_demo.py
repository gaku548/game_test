"""
デモスクリプト - エージェントを複数サイクル実行してGDScriptを生成
"""

from orchestrator import Orchestrator
import time


def main():
    print("\n" + "="*60)
    print("Guild Master Pennant - Demo")
    print("="*60 + "\n")

    orchestrator = Orchestrator()

    # 複数サイクル実行してすべてのGDScriptを生成
    print("Running agents for 3 cycles to generate all GDScript files...\n")

    for cycle in range(3):
        print(f"\n--- Cycle {cycle + 1} ---")
        orchestrator.run_single_cycle()
        time.sleep(0.5)

    # 進捗レポートを表示
    print("\n")
    orchestrator.print_progress()

    # 生成されたファイルを確認
    files = orchestrator.blackboard.get_generated_files()
    print(f"\n✅ Successfully generated {len(files)} GDScript files!\n")

    # Blackboardをエクスポート
    orchestrator.blackboard.export_to_json("blackboard_export.json")
    print("📝 Exported blackboard to blackboard_export.json\n")


if __name__ == "__main__":
    main()
