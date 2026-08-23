#!/usr/bin/env bash
# JojoNowhere AI 剪輯環境安裝腳本
# 冪等：重複執行安全，已裝好的東西會跳過。
set -e

echo "=== JojoNowhere AI 剪輯環境安裝 ==="
echo ""

if ! command -v brew >/dev/null 2>&1; then
  echo "找不到 Homebrew，請先到 https://brew.sh 安裝，再重新執行這支腳本。"
  exit 1
fi

echo "--- 1/5 基礎工具 ---"
for pkg in git uv node ffmpeg; do
  if brew list --formula "$pkg" >/dev/null 2>&1; then
    echo "已安裝: $pkg"
  else
    echo "安裝中: $pkg"
    brew install "$pkg"
  fi
done

echo ""
echo "--- 2/5 video-use（剪輯引擎，MIT授權，來自 browser-use） ---"
VIDEO_USE_DIR="$HOME/Developer/video-use"
if [ -d "$VIDEO_USE_DIR" ]; then
  echo "已存在: $VIDEO_USE_DIR"
else
  git clone https://github.com/browser-use/video-use.git "$VIDEO_USE_DIR"
fi
(cd "$VIDEO_USE_DIR" && uv sync)

# video-use 的轉寫腳本目前上游版本寫死用舊的 scribe_v1，準確度明顯較差。
# 這是第三方repo，每次重新clone都會被還原，所以每次跑setup都要重新檢查/修正這行。
TRANSCRIBE_PY="$VIDEO_USE_DIR/helpers/transcribe.py"
if [ -f "$TRANSCRIBE_PY" ]; then
  if grep -q '"model_id": "scribe_v1"' "$TRANSCRIBE_PY"; then
    echo "修正: video-use 轉寫腳本 model_id (scribe_v1 -> scribe_v2)"
    sed -i '' 's/"model_id": "scribe_v1"/"model_id": "scribe_v2"/' "$TRANSCRIBE_PY"
  else
    echo "video-use 轉寫腳本 model_id 已是正確版本"
  fi
fi

echo ""
echo "--- 3/5 思源黑體 TW 字幕字體（SIL Open Font License，來自 Adobe 官方 repo） ---"
FONT_DIR="$HOME/Library/Fonts"
FONT_SRC="https://github.com/adobe-fonts/source-han-sans/raw/release/SubsetOTF/TW"
mkdir -p "$FONT_DIR"
for weight in Regular Bold; do
  f="$FONT_DIR/SourceHanSansTW-$weight.otf"
  if [ -f "$f" ]; then
    echo "已存在: $f"
  else
    echo "下載中: $weight"
    curl -fL --proto '=https' -o "$f" "$FONT_SRC/SourceHanSansTW-$weight.otf"
  fi
done

echo ""
echo "--- 4/5 /watch plugin（選用，分析參考影片風格用，見 rules/10） ---"
if ! command -v claude >/dev/null 2>&1; then
  echo "沒偵測到 claude 這個獨立CLI指令（例如目前只有Claude桌面版），跳過這步。"
  echo "之後想裝的話：先安裝 Claude Code CLI（npm install -g @anthropic-ai/claude-code），"
  echo "再執行：claude plugin marketplace add bradautomates/claude-video && claude plugin install watch@claude-video"
elif claude plugin list 2>/dev/null | grep -q "watch@claude-video"; then
  echo "已安裝: watch@claude-video"
else
  echo "安裝中: watch@claude-video plugin（MIT授權，來自 bradautomates，非Anthropic官方）"
  claude plugin marketplace add bradautomates/claude-video
  claude plugin install watch@claude-video
fi
if command -v brew >/dev/null 2>&1; then
  if brew list --formula yt-dlp >/dev/null 2>&1; then
    echo "已安裝: yt-dlp"
  else
    echo "安裝中: yt-dlp（/watch下載影片用）"
    brew install yt-dlp
  fi
fi

echo ""
echo "--- 5/5 ElevenLabs API Key（逐字稿轉寫用，付費API，每人要自己申請） ---"
if [ -n "$ELEVENLABS_API_KEY" ]; then
  echo "偵測到 ELEVENLABS_API_KEY 已設定，跳過。"
else
  cat <<'EOF'
還差最後一步，這步要你自己手動做（金鑰不能透過對話或腳本自動設定）：

1. 到 https://elevenlabs.io/app/settings/api-keys 登入/註冊，建立一組新的 API Key
   （有免費額度，一般短片夠用；用量大才會產生費用）
2. 打開你的 shell 設定檔案，例如：
     nano ~/.zshrc
3. 加一行（換成你剛拿到的金鑰，開頭應該是 sk_）：
     export ELEVENLABS_API_KEY="sk_你的金鑰"
4. 存檔後執行：
     source ~/.zshrc

設定好之後，重新執行這支腳本會顯示「已設定」，代表完成。
EOF
fi

echo ""
echo "=== 安裝完成 ==="
