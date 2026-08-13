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

## 裡面有什麼

```
├── SKILL.md                          ← 給AI看的操作流程總覽
├── setup.sh                          ← 環境安裝腳本
└── rules/
    ├── 01-剪輯節奏與轉場規則.md
    ├── 02-多機位同步規則.md            ← 多鏡位（口播＋螢幕錄影）同步對齊
    ├── 03-Premiere-XML規則.md         ← 產生Premiere可匯入的剪輯序列
    └── 04-字幕產生規則.md              ← 斷句、標點、繁體中文輸出規則
```

所有規則都是實際剪片、反覆除錯後歸納出來的，不是憑空寫的規格書。

## 授權

本repo（`SKILL.md`、`rules/`、`setup.sh`）採用 [MIT License](LICENSE)。

實際運作會依賴幾個外部開源工具跟一個付費API，各自授權/條款不同，詳見 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
