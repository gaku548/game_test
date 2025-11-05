"""
Orchestrator - マルチエージェント統括システム

すべてのエージェントを管理し、自律的な開発プロセスを調整する。
"""

import logging
import sys
import threading
import time
from typing import List, Optional

from blackboard import Blackboard
from agents import (
    AdventurerAgent,
    CombatAgent,
    TacticsAgent,
    PartyAgent,
    SkillAgent,
    DungeonAgent
)


class Orchestrator:
    """
    マルチエージェントシステムのオーケストレーター

    責務:
    - エージェントの起動と停止
    - エージェント間の調整
    - 進捗監視
    - 対話モードの提供
    """

    def __init__(self):
        self.blackboard = Blackboard()
        self.agents = []
        self.agent_threads = []
        self.is_running = False

        # ロギング設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("Orchestrator")

        # エージェントを作成
        self._initialize_agents()

    def _initialize_agents(self) -> None:
        """
        すべてのエージェントを初期化
        """
        self.logger.info("Initializing agents...")

        self.agents = [
            AdventurerAgent(self.blackboard),
            CombatAgent(self.blackboard),
            TacticsAgent(self.blackboard),
            PartyAgent(self.blackboard),
            SkillAgent(self.blackboard),
            DungeonAgent(self.blackboard)
        ]

        self.logger.info(f"Initialized {len(self.agents)} agents")

    def start_agents(self, duration: Optional[float] = None) -> None:
        """
        すべてのエージェントを起動

        Args:
            duration: 実行時間（秒）。Noneの場合は手動停止まで実行
        """
        if self.is_running:
            self.logger.warning("Agents are already running")
            return

        self.is_running = True
        self.logger.info("Starting all agents...")

        # 各エージェントを別スレッドで実行
        for agent in self.agents:
            thread = threading.Thread(
                target=agent.run_loop,
                args=(duration,),
                daemon=True
            )
            thread.start()
            self.agent_threads.append(thread)

        self.logger.info("All agents started")

    def stop_agents(self) -> None:
        """
        すべてのエージェントを停止
        """
        if not self.is_running:
            self.logger.warning("Agents are not running")
            return

        self.logger.info("Stopping all agents...")

        for agent in self.agents:
            agent.stop()

        # スレッドの終了を待つ
        for thread in self.agent_threads:
            thread.join(timeout=2.0)

        self.agent_threads.clear()
        self.is_running = False

        self.logger.info("All agents stopped")

    def run_single_cycle(self) -> None:
        """
        すべてのエージェントの think() を1回実行
        """
        self.logger.info("Running single cycle...")

        for agent in self.agents:
            agent.start()
            agent.run_once()

        self.logger.info("Single cycle completed")

    def get_progress(self) -> dict:
        """
        全体の進捗を取得
        """
        summary = self.blackboard.get_summary()
        tasks = self.blackboard.get_all_tasks()

        # エージェントの状態
        agent_statuses = {}
        for agent in self.agents:
            agent_statuses[agent.name] = agent.get_status()

        return {
            "blackboard_summary": summary,
            "tasks": tasks,
            "agent_statuses": agent_statuses
        }

    def print_progress(self) -> None:
        """
        進捗を表示
        """
        progress = self.get_progress()

        print("\n" + "="*60)
        print("PROGRESS REPORT")
        print("="*60)

        # Blackboard要約
        summary = progress["blackboard_summary"]
        print(f"\n📊 Blackboard Summary:")
        print(f"  Messages: {summary['total_messages']}")
        print(f"  Generated Files: {summary['total_files']}")
        print(f"  Decisions: {summary['total_decisions']}")
        print(f"  Tasks: {summary['total_tasks']} (Completed: {summary['completed_tasks']}, Failed: {summary['failed_tasks']})")

        # タスク状態
        print(f"\n✅ Tasks:")
        for task_name, task_info in progress["tasks"].items():
            status_icon = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅",
                "failed": "❌"
            }.get(task_info.get("status"), "❓")

            print(f"  {status_icon} {task_name}: {task_info.get('status')}")
            if task_info.get("details"):
                print(f"      {task_info.get('details')}")

        # エージェント状態
        print(f"\n🤖 Agents:")
        for agent_name, status in progress["agent_statuses"].items():
            print(f"  • {agent_name}")
            print(f"      Role: {status.get('role')}")
            print(f"      Initialized: {status.get('initialized', False)}")
            print(f"      GDScript Generated: {status.get('gdscript_generated', False)}")

        # 生成されたファイル
        files = self.blackboard.get_generated_files()
        if files:
            print(f"\n📄 Generated Files:")
            for filepath, file_info in files.items():
                print(f"  • {filepath}")
                print(f"      by {file_info['agent']}: {file_info['description']}")

        print("\n" + "="*60 + "\n")

    def interactive_mode(self) -> None:
        """
        対話モード - ユーザーと対話しながら開発を進める
        """
        print("\n" + "="*60)
        print("Guild Master Pennant - Multi-Agent Development System")
        print("="*60)
        print("\nCommands:")
        print("  start [duration]  - Start all agents (optional duration in seconds)")
        print("  stop              - Stop all agents")
        print("  cycle             - Run one think() cycle for all agents")
        print("  progress          - Show progress report")
        print("  status            - Show agent statuses")
        print("  messages [agent]  - Show messages (optional: filter by agent)")
        print("  files             - Show generated files")
        print("  export [file]     - Export blackboard to JSON")
        print("  help              - Show this help")
        print("  quit              - Exit")
        print()

        while True:
            try:
                command = input("orchestrator> ").strip().lower()

                if not command:
                    continue

                parts = command.split()
                cmd = parts[0]

                if cmd == "start":
                    duration = float(parts[1]) if len(parts) > 1 else None
                    self.start_agents(duration)

                elif cmd == "stop":
                    self.stop_agents()

                elif cmd == "cycle":
                    self.run_single_cycle()

                elif cmd == "progress":
                    self.print_progress()

                elif cmd == "status":
                    self._show_agent_statuses()

                elif cmd == "messages":
                    agent_filter = parts[1] if len(parts) > 1 else None
                    self._show_messages(agent_filter)

                elif cmd == "files":
                    self._show_files()

                elif cmd == "export":
                    filepath = parts[1] if len(parts) > 1 else "blackboard_export.json"
                    self.blackboard.export_to_json(filepath)
                    print(f"✅ Exported to {filepath}")

                elif cmd == "help":
                    print("\nCommands:")
                    print("  start [duration]  - Start all agents")
                    print("  stop              - Stop all agents")
                    print("  cycle             - Run one cycle")
                    print("  progress          - Show progress")
                    print("  status            - Show agent statuses")
                    print("  messages [agent]  - Show messages")
                    print("  files             - Show generated files")
                    print("  export [file]     - Export blackboard")
                    print("  quit              - Exit")

                elif cmd in ["quit", "exit"]:
                    self.stop_agents()
                    print("Goodbye!")
                    break

                else:
                    print(f"Unknown command: {cmd}. Type 'help' for commands.")

            except KeyboardInterrupt:
                print("\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"Error: {e}")

    def _show_agent_statuses(self) -> None:
        """
        エージェントの状態を表示
        """
        print("\n🤖 Agent Statuses:")
        for agent in self.agents:
            status = agent.get_status()
            active_icon = "🟢" if agent.is_active() else "🔴"
            print(f"\n{active_icon} {agent.name}")
            print(f"  Role: {status.get('role')}")
            print(f"  Active: {agent.is_active()}")
            for key, value in status.items():
                if key not in ["name", "role"]:
                    print(f"  {key}: {value}")

    def _show_messages(self, agent_filter: Optional[str] = None) -> None:
        """
        メッセージを表示
        """
        messages = self.blackboard.get_messages(recipient=agent_filter)

        print(f"\n💬 Messages (Total: {len(messages)}):")
        for msg in messages[-20:]:  # 最新20件
            print(f"\n[{msg['timestamp']}] {msg['sender']} → {msg['recipient']}")
            print(f"  Type: {msg['type']}")
            print(f"  Content: {msg['content'][:100]}...")

    def _show_files(self) -> None:
        """
        生成されたファイルを表示
        """
        files = self.blackboard.get_generated_files()

        print(f"\n📄 Generated Files (Total: {len(files)}):")
        for filepath, file_info in files.items():
            print(f"\n• {filepath}")
            print(f"  Agent: {file_info['agent']}")
            print(f"  Description: {file_info['description']}")
            print(f"  Timestamp: {file_info['timestamp']}")
            print(f"  Lines: {len(file_info['content'].splitlines())}")


def main():
    """
    メイン関数
    """
    orchestrator = Orchestrator()

    # コマンドライン引数に応じて動作を変更
    if len(sys.argv) > 1:
        if sys.argv[1] == "--auto":
            # 自動実行モード
            print("Running in auto mode...")
            orchestrator.run_single_cycle()
            orchestrator.print_progress()
        elif sys.argv[1] == "--run":
            # 一定時間実行
            duration = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0
            print(f"Running for {duration} seconds...")
            orchestrator.start_agents(duration)
            time.sleep(duration + 1)
            orchestrator.print_progress()
    else:
        # 対話モード
        orchestrator.interactive_mode()


if __name__ == "__main__":
    main()
