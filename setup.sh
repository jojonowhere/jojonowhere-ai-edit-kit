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

echo "--- 1/4 基礎工具 ---"
for pkg in git uv node ffmpeg; do
  if brew list --formula "$pkg" >/dev/null 2>&1; then
    echo "已安裝: $pkg"
  else
    echo "安裝中: $pkg"
    brew install "$pkg"
  fi
done

echo ""
echo "--- 2/4 video-use（剪輯引擎，MIT授權，來自 browser-use） ---"
VIDEO_USE_DIR="$HOME/Developer/video-use"
if [ -d "$VIDEO_USE_DIR" ]; then
  echo "已存在: $VIDEO_USE_DIR"
else
  git clone https://github.com/browser-use/video-use.git "$VIDEO_USE_DIR"
fi
(cd "$VIDEO_USE_DIR" && uv sync)

echo ""
echo "--- 3/4 思源黑體 TW 字幕字體（SIL Open Font License，來自 Adobe 官方 repo） ---"
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
echo "--- 4/4 ElevenLabs API Key（逐字稿轉寫用，付費API，每人要自己申請） ---"
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
