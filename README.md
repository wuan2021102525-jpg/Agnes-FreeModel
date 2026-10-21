# Agnes FreeModel

使用 Agnes AI API 產生圖片、編輯圖片與生成影片的 Skill，優先使用最新免費模型，並在模型明確不可用時依序呼叫舊版免費模型。

目前版本：**1.1.0**。基於 agnes-gen 1.0.0 修改，使用 Python 標準庫，無須安裝第三方 Python 套件。

## 功能與模型

| 功能 | 優先模型 | 備用順序 |
| --- | --- | --- |
| 文生圖、圖生圖、多圖合成 | `agnes-image-2.5-flash` | `agnes-image-2.1-flash` → `agnes-image-2.0-flash` |
| 文生影片、圖生影片 | `agnes-video-2.5-flash` | 目前無已確認免費的舊版備援 |

圖片可自動下載；影片支援非同步建立、續查與下載，固定使用 720P，支援 4–12 秒與多種畫幅。

價格查證日期：**2026-10-21**。影片為限時免費優惠，使用前請核對 [官方定價](https://www.agnes-ai.com/zh-Hans/docs/pricing) 與帳戶權限。免費不代表不限量或永久免費。

程式使用固定模型清單，不會自動搜尋未來版本，也不會自動轉用付費模型。舊版 `agnes-video-v2.0` 尚未確認目前免費，未納入備援。本 Skill 不包含文字聊天功能。

## 快速開始

需要 Python 3.8 或更新版本，以及可存取 Agnes AI API 的網路環境。

```bash
git clone https://github.com/wuan2021102525-jpg/Agnes-FreeModel.git
cd Agnes-FreeModel
```

從 [Agnes AI 平台](https://platform.agnes-ai.com/) 取得 API Key，建議設定環境變數。

PowerShell：

```powershell
$env:AGNES_API_KEY = "YOUR_AGNES_API_KEY"
```

macOS / Linux：

```bash
export AGNES_API_KEY="YOUR_AGNES_API_KEY"
```

也支援根目錄 `config.json` 的 `api_key` 欄位，以及根目錄 `.env` 中的 `AGNES_API_KEY`。載入順序為 **環境變數 → config.json → .env**。不要將真實金鑰提交至 GitHub 或包含在分享檔案中。

以下指令均在儲存庫根目錄執行。

## 使用範例

### 文生圖

```bash
python scripts/generate.py image --mode txt2img --prompt "雨後的台北街道，霓虹燈倒映在路面，電影攝影風格" --size 1024x1024 --output ./results
```

程式會顯示實際呼叫的模型、圖片網址與儲存位置。

### 圖片編輯

```bash
python scripts/generate.py image --mode img2img --prompt "保留人物與構圖，將背景改為黃昏海邊" --image "https://example.com/source.png" --output ./results
```

多圖合成可重複提供 `--image`：

```bash
python scripts/generate.py image --mode img2img --prompt "將兩個角色放入同一個場景" --image "https://example.com/a.png" --image "https://example.com/b.png" --output ./results
```

範例網址需替換為 Agnes AI 服務可存取的實際圖片網址。

### 生成影片並等待下載

```bash
python scripts/generate.py video --prompt "一隻貓在陽光下的草地奔跑，鏡頭平穩跟隨" --seconds 5 --aspect-ratio 16:9 --output ./results
```

### 只建立影片任務

`create` 提交後立即返回 `video_id`。提供 `--image` 時，圖片會作為影片首幀。

```bash
python scripts/generate.py create --prompt "讓角色緩緩向前走" --image "https://example.com/source.png" --seconds 5 --aspect-ratio 9:16
```

### 續查與下載

使用建立任務時回傳的 **video_id**，不能使用 task_id。

```bash
python scripts/generate.py poll --video-id video_xxx --output ./results
```

只顯示完成後的網址、不下載：

```bash
python scripts/generate.py poll --video-id video_xxx --no-download
```

## 常用參數

| 指令 | 參數 | 說明 |
| --- | --- | --- |
| image | `--mode` | 必填：txt2img 或 img2img |
| image / video / create | `--prompt` | 必填：提示詞 |
| image | `--image` | 圖生圖必填，可重複提供多張 |
| image | `--size` | 預設 1024x1024；亦可使用 1024x768、768x1024 |
| image | `--seed` | 選填整數；不保證完全重現結果 |
| video / create | `--image` | 選填，作為影片首幀 |
| video / create | `--seconds` | 4–12 的整數，預設 5 |
| video / create | `--aspect-ratio` | 21:9、16:9、4:3、1:1、3:4、9:16；預設 16:9 |
| poll | `--video-id` | 必填：影片 ID |
| poll | `--no-download` | 完成後只顯示網址 |
| image / video / poll | `--output` | 輸出資料夾；預設為 Skill 根目錄的 generated-images |

新版影片已改用 `--seconds`、`--aspect-ratio` 與 `--video-id`，不再使用 `--num-frames`、`--frame-rate`、`--height`、`--width` 或 `--task-id`。

```bash
python scripts/generate.py --help
python scripts/generate.py image --help
python scripts/generate.py video --help
```

## 備援與錯誤處理

僅在 API 明確拒絕建立，且錯誤指出模型不存在、不可用、已退役或無該模型權限時，才嘗試下一個免費圖片模型。成功即停止，每個候選最多一次。

- **401**：檢查金鑰與帳戶狀態。
- **一般 400**：修正參數；內容安全拒絕不以換模型重試。
- **429**：檢查配額及請求頻率，不自動換模型。
- **建立時伺服器錯誤或連線逾時**：可能已接受任務，先查平台狀態，避免重複提交。
- **影片輪詢**：暫時性 HTTP 錯誤會等待後續查，最多 600 次；達上限可用原 video_id 再次查詢。

取得影片 ID 後只查原任務，不會重新建立。完成後使用回應的頂層 `url` 下載。

## 作為 Skill 使用

[SKILL.md](SKILL.md) 為入口，包含工作流程與模型選擇規則。依所使用工具的 Skill 載入方式匯入本目錄；下載或 clone 不會自行安裝。

載入後可提出自然語言任務，例如：

> 使用 Agnes AI 產生一張未來城市圖片，優先使用最新免費模型。

## 檔案結構

```text
Agnes-FreeModel/
├── README.md
├── SKILL.md
├── skill.json
├── _meta.json
├── config.json
├── scripts/
│   └── generate.py
└── references/
    └── api_reference.md
```

## 驗證與來源

已通過 Skill 格式驗證，以及備援順序、錯誤停止、影片請求、查詢與輪詢上限的模擬測試。**尚未進行真實 API 呼叫測試。**

- [API 參考摘要](references/api_reference.md)
- [Agnes AI 官方文件](https://www.agnes-ai.com/zh-Hans/docs/overview)
- [圖片模型文件](https://www.agnes-ai.com/zh-Hans/docs/agnes-image-25-flash)
- [影片模型文件](https://www.agnes-ai.com/zh-Hans/docs/agnes-video-25-flash)
- [官方模型儲存庫](https://github.com/AgnesAI-Labs/AgnesAI-Models)

本專案為修改版本，與 Agnes AI 官方無隸屬關係。
