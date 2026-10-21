---
name: agnes-ai
description: 使用 Agnes AI 免費 API 產生或編輯圖片、從文字或圖片生成影片。優先最新免費模型，舊版免費圖片模型依序備援；適用於使用者指定 Agnes AI 的生成任務。
---

# Agnes AI 圖片與影片生成

此版本基於 agnes-gen 1.0.0 修改，保留純 Python 標準庫、圖片下載、影片建立與輪詢功能。模型價格查證日期為 2026-10-21，使用前核對 [官方定價](https://www.agnes-ai.com/zh-Hans/docs/pricing) 與帳戶權限，確認目前仍免費。價格無法確認或優惠結束時停止呼叫，不自動轉付費模型。

## 模型優先順序

- 文生圖、圖生圖與多圖合成：agnes-image-2.5-flash → agnes-image-2.1-flash → agnes-image-2.0-flash。
- 文生影片、圖生影片：agnes-video-2.5-flash（720P）。agnes-video-v2.0 未在目前定價頁確認免費，因此不啟用為備用；agnes-video-2.5 為付費。
- 本 Skill 原有功能為圖片與影片，不擴充文字聊天。

模型與來源見 [references/api_reference.md](references/api_reference.md)。將來更新時只加入官方已上線、用途相容且價格為零的完整 model ID，同系列以數字版本由新至舊排序，同時修改程式常數及文件。

## 設定

建議使用 AGNES_API_KEY 環境變數。相容原有 config.json 的 api_key 欄位及 Skill 目錄內 .env；載入優先順序為環境變數 → config.json → .env。不要把真實金鑰包含在分享的 ZIP 或輸出內容。

Base URL：https://apihub.agnes-ai.com/v1。

## 使用

以下指令中的 scripts/generate.py 須相對於本 Skill 目錄執行。

文生圖：
    python scripts/generate.py image --mode txt2img --prompt "雨後城市" --size 1024x1024 --output ./results

圖生圖（可重複 --image 做多圖合成）：
    python scripts/generate.py image --mode img2img --prompt "改為黃昏" --image "https://example.com/source.png" --output ./results

影片建立並下載：
    python scripts/generate.py video --prompt "貓在草地奔跑" --seconds 5 --aspect-ratio 16:9 --output ./results

圖生影片只需加上 --image 公開圖片 URL，會映射為 keyframe 模式的 first_frame。建立後立即返回：
    python scripts/generate.py create --prompt "讓角色向前走" --image "https://example.com/source.png" --seconds 5

續查：
    python scripts/generate.py poll --video-id video_xxx --output ./results

舊影片參數 --num-frames、--frame-rate、--height、--width 已改為 --seconds（4–12 整數）及 --aspect-ratio；查詢改用 --video-id，不能傳 task_id。

## 備援與失敗處理

程式僅在 API 明確拒絕建立、且錯誤內容指明模型不存在／不可用／已退役或無模型權限時，依序嘗試下一個免費模型。成功即停止，每個候選最多一次。
401、一般 400、內容安全拒絕、429、伺服器或網路錯誤不自動切換。伺服器錯誤或建立逾時可能已接受任務，先查平台，不盲目重送。不要藉換模型繞過帳戶配額或內容安全限制。
取得 video_id 後只查原任務，最多輪詢 600 次；達上限保留 ID 供續查。暫時性輪詢 HTTP 錯誤退避，其他錯誤立即停止。影片完成使用頂層 url 下載。
回報實際模型與輸出位置；無法取得免費且相容的模型則說明原因。此版本不會自行安裝或修改其他 Skill。
