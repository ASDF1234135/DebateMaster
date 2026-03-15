import os
import asyncio
import uuid
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv


load_dotenv()


class DebateDBWriter:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("POSTGRES_DB", "postgres"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        )
        self.conn.autocommit = False

    def close(self) -> None:
        if self.conn:
            self.conn.close()

    def commit(self) -> None:
        self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

    def insert_session(self, config: Dict[str, Any]) -> None:
        sql = """
        INSERT INTO debate_sessions (
            session_id,
            prompt,
            context,
            file_name,
            opponent_persona,
            my_persona,
            max_rounds,
            trial
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (session_id) DO NOTHING
        """
        values = (
            config["session_id"],
            config["prompt"],
            config.get("context"),
            config.get("file_name"),
            config.get("opponent_persona"),
            config.get("my_persona"),
            config["max_rounds"],
            config["trial"],
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, values)

    def insert_message(self, session_id: str, event: Dict[str, Any], sequence_no: int) -> None:
        sql = """
        INSERT INTO debate_messages (
            session_id,
            type,
            speaker,
            round,
            trial,
            content,
            sequence_no
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            session_id,
            event["type"],
            event["speaker"],
            event["round"],
            event["trial"],
            event["content"],
            sequence_no,
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, values)

    def insert_summary(self, session_id: str, event: Dict[str, Any]) -> None:
        sql = """
        INSERT INTO debate_summaries (
            session_id,
            type,
            speaker,
            pros,
            cons,
            improvement_tips
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (session_id)
        DO UPDATE SET
            type = EXCLUDED.type,
            speaker = EXCLUDED.speaker,
            pros = EXCLUDED.pros,
            cons = EXCLUDED.cons,
            improvement_tips = EXCLUDED.improvement_tips
        """
        values = (
            session_id,
            event["type"],
            event["speaker"],
            Json(event["pros"]),
            Json(event["cons"]),
            Json(event["improvement_tips"]),
        )

        with self.conn.cursor() as cur:
            cur.execute(sql, values)

    def get_sessions(self) -> List[Dict[str, Any]]:
        sql = """
        SELECT
            session_id,
            prompt,
            my_persona,
            opponent_persona,
            max_rounds,
            trial
        FROM debate_sessions
        ORDER BY session_id DESC
        """

        with self.conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

        results: List[Dict[str, Any]] = []
        for row in rows:
            results.append({
                "session_id": row[0],
                "prompt": row[1],
                "my_persona": row[2],
                "opponent_persona": row[3],
                "max_round": row[4],
                "max_trial": row[5],
            })

        return results

    def get_messages_and_summary(self, session_id: str) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []

        message_sql = """
        SELECT
            type,
            speaker,
            round,
            trial,
            content,
            sequence_no
        FROM debate_messages
        WHERE session_id = %s
        ORDER BY sequence_no ASC
        """

        summary_sql = """
        SELECT
            type,
            speaker,
            pros,
            cons,
            improvement_tips
        FROM debate_summaries
        WHERE session_id = %s
        """

        with self.conn.cursor() as cur:
            cur.execute(message_sql, (session_id,))
            message_rows = cur.fetchall()

            for row in message_rows:
                results.append({
                    "type": row[0],
                    "speaker": row[1],
                    "round": row[2],
                    "trial": row[3],
                    "content": row[4],
                })

            cur.execute(summary_sql, (session_id,))
            summary_row = cur.fetchone()

            if summary_row:
                results.append({
                    "type": summary_row[0],
                    "speaker": summary_row[1],
                    "pros": summary_row[2] if summary_row[2] is not None else [],
                    "cons": summary_row[3] if summary_row[3] is not None else [],
                    "improvement_tips": summary_row[4] if summary_row[4] is not None else [],
                })

        return results

    def getSessions(self) -> List[Dict[str, Any]]:
        return self.get_sessions()

    def getMessagesAndSummary(self, session_id: str) -> List[Dict[str, Any]]:
        return self.get_messages_and_summary(session_id)


def normalize_session_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 session 設定整理成符合 debate_sessions schema 的格式
    """
    return {
        "session_id": str(config.get("session_id") or uuid.uuid4()),
        "prompt": str(config["prompt"]),
        "context": config.get("context"),
        "file_name": config.get("file_name"),
        "opponent_persona": config.get("opponent_persona"),
        "my_persona": config.get("my_persona"),
        "max_rounds": int(config["max_rounds"]),
        "trial": int(config["trial"]),
    }


def normalize_conversation_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 AI conversation event 清洗成符合 debate_messages schema 的格式
    """
    return {
        "type": "conversation",
        "speaker": str(event["speaker"]),
        "round": int(event["round"]),
        "trial": int(event["trial"]),
        "content": str(event["content"]),
    }


def normalize_point_list(points: Any) -> List[Dict[str, Any]]:
    """
    將 pros / cons 統一轉成 list[dict]
    可處理：
    - 已經是 dict
    - Pydantic model
    - 一般物件
    """
    normalized: List[Dict[str, Any]] = []

    if not points:
        return normalized

    for item in points:
        if isinstance(item, dict):
            normalized.append({
                "point": item.get("point"),
                "severity": item.get("severity"),
                "description": item.get("description"),
            })
        elif hasattr(item, "model_dump"):
            dumped = item.model_dump()
            normalized.append({
                "point": dumped.get("point"),
                "severity": dumped.get("severity"),
                "description": dumped.get("description"),
            })
        else:
            normalized.append({
                "point": getattr(item, "point", None),
                "severity": getattr(item, "severity", None),
                "description": getattr(item, "description", None),
            })

    return normalized


def normalize_summary_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    將 AI summary event 清洗成符合 debate_summaries schema 的格式
    """
    return {
        "type": "summary",
        "speaker": str(event.get("speaker", "agent_judge")),
        "pros": normalize_point_list(event.get("pros", [])),
        "cons": normalize_point_list(event.get("cons", [])),
        "improvement_tips": [str(tip) for tip in event.get("improvement_tips", [])],
    }


async def run_and_save() -> None:
    mock_config = {
        "session_id": f"test_session_{uuid.uuid4().hex[:8]}",
        "context": "公司近期為了節省營運成本，正在評估辦公空間的縮減計畫。但跨部門溝通的效率一直是管理層的隱憂。",
        "prompt": "我主張公司應該全面導入『每週三天遠端、兩天進辦公室』的混合辦公模式 (Hybrid Work)，這不僅能省下租金，還能提升員工留任率。",
        "my_persona": "一位注重數據佐證、強調數位協作工具效率的年輕專案經理。",
        "opponent_persona": "一位傳統、極度重視「實體見面三分情」與隨機腦力激盪的資深營運總監，對遠端工作抱持高度不信任。",
        "max_rounds": 1,
        "trial": 1,
        "file_name": None,
    }

    config = normalize_session_config(mock_config)

    db = DebateDBWriter()
    sequence_no = 1

    try:
        print("🚀 開始寫入 debate_sessions ...")
        db.insert_session(config)
        db.commit()
        print(f"✅ session 已建立: {config['session_id']}")

        print("🥊 開始接收 AI 事件並寫入資料庫...\n")

        async for raw_event in run_debate(config):
            event_type = raw_event.get("type")

            if event_type == "init":
                print("ℹ️ init event 收到（不寫入 DB）")
                print(f"pro_sys_prompt: {raw_event['pro_sys_prompt'][:80]}...")
                print(f"con_sys_prompt: {raw_event['con_sys_prompt'][:80]}...\n")

            elif event_type == "conversation":
                event = normalize_conversation_event(raw_event)

                db.insert_message(config["session_id"], event, sequence_no)
                db.commit()

                print(
                    f"✅ message 已寫入 | "
                    f"speaker={event['speaker']} | "
                    f"round={event['round']} | "
                    f"trial={event['trial']} | "
                    f"sequence_no={sequence_no}"
                )
                sequence_no += 1

            elif event_type == "summary":
                event = normalize_summary_event(raw_event)

                db.insert_summary(config["session_id"], event)
                db.commit()

                print("✅ summary 已寫入 debate_summaries")
                print("🎉 全部完成")

            else:
                print(f"⚠️ 未知 event type，略過: {event_type}")

    except Exception as e:
        db.rollback()
        print(f"❌ 寫入資料庫失敗: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_and_save())