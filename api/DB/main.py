import uuid
from save_debate_to_db import DebateDBWriter


def insert_mock_data() -> str:
    db = DebateDBWriter()
    session_id = str(uuid.uuid4())

    mock_session = {
        "session_id": session_id,
        "prompt": "我主張公司應該全面導入混合辦公模式。",
        "context": "公司正在評估辦公空間縮減計畫。",
        "file_name": None,
        "opponent_persona": "一位傳統的資深營運總監",
        "my_persona": "一位注重數據佐證的年輕專案經理",
        "max_rounds": 2,
        "trial": 1,
    }

    mock_message_1 = {
        "type": "conversation",
        "speaker": "agent_pro",
        "round": 1,
        "trial": 1,
        "content": "我認為混合辦公模式可以降低租金成本。",
    }

    mock_message_2 = {
        "type": "conversation",
        "speaker": "agent_con",
        "round": 1,
        "trial": 1,
        "content": "但你忽略了實體協作效率下降的風險。",
    }

    mock_summary = {
        "type": "summary",
        "speaker": "agent_judge",
        "pros": [
            {
                "point": "成本節省",
                "severity": "low",
                "description": "正方有明確提出節省租金的優勢。"
            }
        ],
        "cons": [
            {
                "point": "協作風險",
                "severity": "high",
                "description": "反方指出溝通與協作效率下降。"
            }
        ],
        "improvement_tips": [
            "補充遠端協作工具的管理方案。"
        ],
    }

    try:
        print("=== 插入 session ===")
        db.insert_session(mock_session)
        db.commit()
        print(f"✅ session inserted: {session_id}")

        print("\n=== 插入 messages ===")
        db.insert_message(session_id, mock_message_1, sequence_no=1)
        db.commit()
        print("✅ message 1 inserted")

        db.insert_message(session_id, mock_message_2, sequence_no=2)
        db.commit()
        print("✅ message 2 inserted")

        print("\n=== 插入 summary ===")
        db.insert_summary(session_id, mock_summary)
        db.commit()
        print("✅ summary inserted")

        return session_id

    except Exception as e:
        db.rollback()
        print(f"❌ insert failed: {e}")
        raise
    finally:
        db.close()


def test_get_sessions():
    db = DebateDBWriter()
    try:
        print("\n=== 測試 getSessions() ===")
        data = db.getSessions()
        print(f"共讀到 {len(data)} 筆 sessions")
        for item in data:
            print(item)
    finally:
        db.close()


def test_get_messages_and_summary(session_id: str):
    db = DebateDBWriter()
    try:
        print(f"\n=== 測試 getMessagesAndSummary({session_id}) ===")
        data = db.getMessagesAndSummary(session_id)
        print(f"共讀到 {len(data)} 筆 records")
        for item in data:
            print(item)
    finally:
        db.close()


if __name__ == "__main__":
    session_id = insert_mock_data()
    test_get_sessions()
    test_get_messages_and_summary(session_id)