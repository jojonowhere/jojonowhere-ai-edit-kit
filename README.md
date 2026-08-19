# JojoNowhere AI Edit Kit

## 關於

我是 Jojo，揪揪漫遊｜JojoNowhere。

我習慣把自己丟進陌生的生態系裡，實測、踩雷、記錄下來分享——希望在使用AI提供工作效率後，不是成為工作狂，而是遊牧享受人生。

這個資源包記錄的是我還在進行中的「用 Claude 打造剪片流程」的實況本身——不是一套已經完成的SOP，是跟我一起做、一起試出來的東西。

免費、開源，揪你一起，慢慢來。

## 安裝

```bash
git clone <這個repo的網址>
cd jojonowhere-ai-edit-kit
bash setup.sh
```

`setup.sh` 會檢查/安裝：`git`、`uv`、`node`、`ffmpeg`（透過Homebrew）、`video-use`（剪輯引擎）、思源黑體 TW 字幕字體。最後會引導你自己申請 ElevenLabs API Key（免費額度，逐字稿轉寫用），這一步不能自動化，需要你自己動手。

## 怎麼用

裝好之後，跟你的 Claude Code 說：

> 請使用 jojonowhere-ai-edit-kit 幫我剪輯 `/路徑/原始影片.mov`

或是只想上字幕：

> 請使用 jojonowhere-ai-edit-kit 幫我這支成品影片上繁體中文字幕

完整操作流程見 [`SKILL.md`](SKILL.md)。

想幫剪好的影片加強調字/貼紙/Logo（選用步驟），用 `tools/cut_planner.html`（「剪接台」）框出位置/大小/時間點，匯出計畫貼給Claude——第一次用這塊，先看 [`新手上路指南.md`](新手上路指南.md)。

## 裡面有什麼

```
├── SKILL.md                          ← 給AI看的操作流程總覽
├── 新手上路指南.md                    ← 給人看的：怎麼用「剪接台」、視覺語言辭典、建議流程
├── setup.sh                          ← 環境安裝腳本
├── tools/
│   └── cut_planner.html              ← 「剪接台」：規劃強調字/貼紙位置、大小、時間點的網頁工具
├── remotion-starter/                 ← Remotion共用元件範本（懸浮光暈卡片、文字量測、字型載入等）
│                                        每支新影片複製一份出去當起點，不要沿用同一份
├── scripts/
│   ├── sync_multicam.py              ← 多機位音訊比對，抓隨時間變化的漂移量（見 02）
│   ├── parse_prproj.py               ← 讀既有Premiere專案，把已剪好的序列反推成EDL JSON
│   ├── digital_zoom.py               ← 逐幀裁切+放大做數位變焦（ffmpeg的crop filter做不到逐幀變化）
│   └── check_alpha.py                ← 驗證Remotion輸出的透明通道，產生黑底/亮底合成預覽（見 08）
└── rules/
    ├── 01-剪輯節奏與轉場規則.md
    ├── 02-多機位同步規則.md            ← 多鏡位（口播＋螢幕錄影）同步對齊
    ├── 03-Premiere-XML規則.md         ← 產生Premiere可匯入的剪輯序列
    ├── 04-字幕產生規則.md              ← 斷句、標點、繁體中文輸出規則
    ├── 05-動畫疊加規則.md              ← 選用，HyperFrames動畫效果（未實測，僅供參考）
    ├── 06-剪接台工具開發規則.md         ← 「剪接台」網頁工具本身的開發規則（只有要改工具才需要）
    ├── 07-懸浮光暈卡片視覺規範.md       ← 疊加素材的固定視覺風格（白框＋光暈＋晃動）
    ├── 08-Remotion算圖管線.md          ← 產生透明通道正式素材的安裝/指令/尺寸規則
    ├── 09-強調字貼紙內容確認規則.md     ← 收到剪接台匯出計畫後，動手前要先問清楚什麼
    └── 10-網路資料查詢規則.md           ← 什麼時候查網路資料、怎麼查、跟已驗證規則衝突時怎麼辦
```

所有規則都是實際剪片、反覆除錯後歸納出來的，不是憑空寫的規格書。

## 授權

本repo（`SKILL.md`、`rules/`、`setup.sh`）採用 [MIT License](LICENSE)。

實際運作會依賴幾個外部開源工具跟一個付費API，各自授權/條款不同，詳見 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
