# 第三方工具與服務

這個資源包本身（`SKILL.md`、`rules/` 底下的所有規則、`setup.sh`）是原創內容，採用本 repo 的 `LICENSE`（MIT）。

實際執行剪輯時會呼叫以下外部工具／服務，各自的授權/條款獨立於本 repo，使用時請遵守它們各自的規定：

| 工具 | 用途 | 授權／性質 |
|---|---|---|
| [video-use](https://github.com/browser-use/video-use) | 逐字稿轉寫、時間碼定位、切檔案的核心引擎 | MIT License，著作權屬 Browser Use |
| [ElevenLabs Scribe v2](https://elevenlabs.io/) | 語音轉文字（逐字稿） | 商業付費 API，非開源；每人須自行申請帳號與 API Key，有免費額度 |
| [FFmpeg](https://ffmpeg.org/) | 影音處理、格式轉換 | LGPL 2.1+（部分編譯選項下為 GPL），非 MIT |
| [Node.js](https://nodejs.org/) | 執行 Claude Code Skills 安裝器 | MIT License |
| [uv](https://github.com/astral-sh/uv) | Python 環境管理 | MIT / Apache 2.0 雙授權 |
| [思源黑體 Source Han Sans（TW子集）](https://github.com/adobe-fonts/source-han-sans) | 繁體中文字幕燒錄字體 | SIL Open Font License 1.1，著作權屬 Adobe |
| [OpenCC](https://github.com/BYVoid/OpenCC) | 簡體轉繁體中文（含台灣用詞） | Apache License 2.0 |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | 選用，動畫疊加效果 | Apache License 2.0，著作權屬原專案；未實測，僅在使用者明確要求動畫效果時才需要 |

本資源包不包含上述任何項目的原始碼副本——`setup.sh` 只會引導安裝或直接從官方來源下載，安裝到你自己的電腦上，使用時請直接遵守各項目自己的授權條款。

這是社群整理的非官方使用流程，跟上述任何公司或專案沒有從屬、贊助或合作關係。
