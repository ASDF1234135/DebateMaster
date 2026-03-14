import asyncio
import json
from core import run_debate

async def main():
    print("🚀 系統啟動：開始初始化 Mock Data...\n")
    
    mock_config = {
        "session_id": "test_session_001",
        "context": "公司近期為了節省營運成本，正在評估辦公空間的縮減計畫。但跨部門溝通的效率一直是管理層的隱憂。",
        "prompt": "我主張公司應該全面導入『每週三天遠端、兩天進辦公室』的混合辦公模式 (Hybrid Work)，這不僅能省下租金，還能提升員工留任率。",
        "my_persona": "一位注重數據佐證、強調數位協作工具效率的年輕專案經理。",
        "opponent_persona": "一位傳統、極度重視「實體見面三分情」與隨機腦力激盪的資深營運總監，對遠端工作抱持高度不信任。",
        "max_rounds": 4, 
        "trial": 1
    }

    print("-" * 50)
    print("🥊 辯論開始！(等待 AI 生成中...)")
    print("-" * 50)

    try:
        async for event in run_debate(mock_config):
            
            if event["type"] == "conversation":
                speaker_name = "🟢 正方 (我)" if event["speaker"] == "agent_pro" else "🔴 反方 (對手)"
                print(f"[{speaker_name} - 回合 {event['round']}]")
                print(f"{event['content']}\n")
                print("- " * 25)
            
            elif event["type"] == "summary":
                print("\n⚖️ [裁判總結報告出爐]")
                print(json.dumps(event, indent=2, ensure_ascii=False))

            elif event["type"] == "init":
                print("\nSystem Prompt")
                print(json.dumps(event, indent=2, ensure_ascii=False))
                
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        print("請確認是否已正確設定 DASHSCOPE_API_KEY 環境變數！")

if __name__ == "__main__":
    asyncio.run(main())