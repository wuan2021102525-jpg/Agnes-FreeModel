# Agnes FreeModel

基於 agnes-gen 1.0.0 修改的 Agnes AI 圖片與影片生成 Skill，目前版本為 1.1.0。

## 模型順序

- 圖片生成、編輯及多圖合成：agnes-image-2.5-flash → agnes-image-2.1-flash → agnes-image-2.0-flash。
- 影片：agnes-video-2.5-flash（720P）。未加入無法確認仍免費的舊版影片模型。
- 僅在 API 明確回報模型不可用時，依序使用免費備用模型。

免費價格查證日期：2026-10-21。使用前請核對 [官方定價](https://www.agnes-ai.com/zh-Hans/docs/pricing)，免費優惠與帳戶權限可能變更。

## 使用

下載 [Skill ZIP](releases/agnes-gen-1.1.0.zip)，或閱讀 [SKILL.md](SKILL.md)。
使用 AGNES_API_KEY 環境變數設定自己的金鑰，勿提交金鑰或 .env。

影片新版參數為 --seconds、--aspect-ratio，續查使用 --video-id。
完整介面與範例請見 SKILL.md 及 references/api_reference.md。

已通過格式驗證與模擬測試，尚未進行真實 API 呼叫。此儲存庫為修改版本，非 Agnes AI 官方發行。
