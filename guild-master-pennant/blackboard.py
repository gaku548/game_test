"""
Blackboard - 共有情報ストア

エージェント間で情報を共有するための中央ストレージシステム。
各エージェントはBlackboardから情報を読み取り、新しい情報を書き込む。
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
import json
from threading import Lock


class Blackboard:
    """
    エージェント間で共有する情報を管理するBlackboard

    主な機能:
    - エージェント間のメッセージング
    - システム状態の共有
    - 生成されたコードの保存
    - 設計決定の記録
    """

    def __init__(self):
        self._data: Dict[str, Any] = {
            "messages": [],           # エージェント間メッセージ
            "generated_files": {},    # 生成されたファイル
            "system_state": {},       # システムの状態
            "decisions": [],          # 設計決定の履歴
            "tasks": {},              # タスクとステータス
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        self._lock = Lock()
        self._subscribers: Dict[str, List[callable]] = {}

    def post_message(self, sender: str, recipient: str, content: str,
                    message_type: str = "info", metadata: Optional[Dict] = None) -> None:
        """
        エージェント間でメッセージを送信

        Args:
            sender: 送信者のエージェント名
            recipient: 受信者のエージェント名 ("all" で全員に送信)
            content: メッセージ内容
            message_type: メッセージタイプ (info, request, response, error)
            metadata: 追加のメタデータ
        """
        with self._lock:
            message = {
                "id": len(self._data["messages"]),
                "timestamp": datetime.now().isoformat(),
                "sender": sender,
                "recipient": recipient,
                "type": message_type,
                "content": content,
                "metadata": metadata or {}
            }
            self._data["messages"].append(message)

            # サブスクライバーに通知
            if recipient in self._subscribers:
                for callback in self._subscribers[recipient]:
                    callback(message)
            if "all" in self._subscribers and recipient == "all":
                for callback in self._subscribers["all"]:
                    callback(message)

    def get_messages(self, recipient: Optional[str] = None,
                    since_id: Optional[int] = None) -> List[Dict]:
        """
        メッセージを取得

        Args:
            recipient: 受信者でフィルタ (None=全メッセージ)
            since_id: 指定したID以降のメッセージのみ取得

        Returns:
            メッセージのリスト
        """
        with self._lock:
            messages = self._data["messages"]

            if since_id is not None:
                messages = [m for m in messages if m["id"] > since_id]

            if recipient is not None:
                messages = [m for m in messages
                          if m["recipient"] == recipient or m["recipient"] == "all"]

            return messages

    def subscribe(self, agent_name: str, callback: callable) -> None:
        """
        メッセージの通知を受け取るために購読

        Args:
            agent_name: エージェント名
            callback: メッセージ受信時に呼ばれる関数
        """
        with self._lock:
            if agent_name not in self._subscribers:
                self._subscribers[agent_name] = []
            self._subscribers[agent_name].append(callback)

    def set_value(self, key: str, value: Any, category: str = "system_state") -> None:
        """
        値を設定

        Args:
            key: キー名
            value: 値
            category: カテゴリ (system_state, generated_files, tasks など)
        """
        with self._lock:
            if category not in self._data:
                self._data[category] = {}
            self._data[category][key] = value

    def get_value(self, key: str, category: str = "system_state",
                 default: Any = None) -> Any:
        """
        値を取得

        Args:
            key: キー名
            category: カテゴリ
            default: デフォルト値

        Returns:
            値
        """
        with self._lock:
            if category not in self._data:
                return default
            return self._data[category].get(key, default)

    def add_generated_file(self, filepath: str, content: str,
                          agent: str, description: str = "") -> None:
        """
        生成されたファイルを記録

        Args:
            filepath: ファイルパス
            content: ファイル内容
            agent: 生成したエージェント名
            description: ファイルの説明
        """
        with self._lock:
            self._data["generated_files"][filepath] = {
                "content": content,
                "agent": agent,
                "description": description,
                "timestamp": datetime.now().isoformat()
            }

    def get_generated_files(self) -> Dict[str, Dict]:
        """
        生成されたすべてのファイルを取得

        Returns:
            {filepath: {content, agent, description, timestamp}}
        """
        with self._lock:
            return dict(self._data["generated_files"])

    def add_decision(self, agent: str, decision: str, rationale: str) -> None:
        """
        設計決定を記録

        Args:
            agent: 決定したエージェント名
            decision: 決定内容
            rationale: 決定理由
        """
        with self._lock:
            self._data["decisions"].append({
                "timestamp": datetime.now().isoformat(),
                "agent": agent,
                "decision": decision,
                "rationale": rationale
            })

    def get_decisions(self, agent: Optional[str] = None) -> List[Dict]:
        """
        設計決定を取得

        Args:
            agent: エージェント名でフィルタ (None=全決定)

        Returns:
            決定のリスト
        """
        with self._lock:
            decisions = self._data["decisions"]
            if agent is not None:
                decisions = [d for d in decisions if d["agent"] == agent]
            return decisions

    def set_task_status(self, task_name: str, status: str,
                       agent: Optional[str] = None, details: str = "") -> None:
        """
        タスクのステータスを更新

        Args:
            task_name: タスク名
            status: ステータス (pending, in_progress, completed, failed)
            agent: 担当エージェント
            details: 詳細情報
        """
        with self._lock:
            if task_name not in self._data["tasks"]:
                self._data["tasks"][task_name] = {
                    "created_at": datetime.now().isoformat()
                }

            self._data["tasks"][task_name].update({
                "status": status,
                "agent": agent,
                "details": details,
                "updated_at": datetime.now().isoformat()
            })

    def get_task_status(self, task_name: str) -> Optional[Dict]:
        """
        タスクのステータスを取得

        Args:
            task_name: タスク名

        Returns:
            タスク情報
        """
        with self._lock:
            return self._data["tasks"].get(task_name)

    def get_all_tasks(self) -> Dict[str, Dict]:
        """
        すべてのタスクを取得

        Returns:
            {task_name: task_info}
        """
        with self._lock:
            return dict(self._data["tasks"])

    def export_to_json(self, filepath: str) -> None:
        """
        Blackboardの内容をJSONファイルにエクスポート

        Args:
            filepath: 出力ファイルパス
        """
        with self._lock:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get_summary(self) -> Dict[str, Any]:
        """
        Blackboardの要約を取得

        Returns:
            要約情報
        """
        with self._lock:
            return {
                "total_messages": len(self._data["messages"]),
                "total_files": len(self._data["generated_files"]),
                "total_decisions": len(self._data["decisions"]),
                "total_tasks": len(self._data["tasks"]),
                "completed_tasks": sum(1 for t in self._data["tasks"].values()
                                      if t.get("status") == "completed"),
                "failed_tasks": sum(1 for t in self._data["tasks"].values()
                                   if t.get("status") == "failed")
            }

    def clear(self) -> None:
        """
        Blackboardをクリア（テスト用）
        """
        with self._lock:
            self._data = {
                "messages": [],
                "generated_files": {},
                "system_state": {},
                "decisions": [],
                "tasks": {},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }
