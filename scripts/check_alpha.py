#!/usr/bin/env python3
"""驗證Remotion渲染出來的ProRes4444素材真的有透明通道，並產生黑底/亮底合成預覽圖。

背景：macOS會自動選用硬體加速的prores_videotoolbox編碼器渲染ProRes，這個編碼器不支援
透明通道，會靜默地把alpha拿掉——不會報錯、影片正常輸出，只有實際疊圖合成時才會發現
背景是黑的不是透明的。渲染指令本身的四個必要參數見 rules/08-Remotion算圖管線.md，
這支腳本是渲染完之後的驗證步驟。

用法：
    python3 check_alpha.py out.mov --frame-time 1.0 --out-dir ./alpha_check
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image


def ffprobe_pix_fmt(video_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=pix_fmt", "-of", "csv=p=0", str(video_path)],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def extract_frame(video_path, frame_time, out_png):
    subprocess.run(
        ["ffmpeg", "-y", "-ss", str(frame_time), "-i", str(video_path),
         "-frames:v", "1", "-pix_fmt", "rgba", str(out_png)],
        capture_output=True, check=True,
    )


def check_corner_alpha(png_path):
    im = Image.open(png_path).convert("RGBA")
    w, h = im.size
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    alphas = [im.getpixel(c)[3] for c in corners]
    return alphas


def composite_on(png_path, bg_rgb, out_path):
    fg = Image.open(png_path).convert("RGBA")
    bg = Image.new("RGBA", fg.size, bg_rgb + (255,))
    composed = Image.alpha_composite(bg, fg)
    composed.convert("RGB").save(out_path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="要檢查的ProRes4444 .mov檔案")
    ap.add_argument("--frame-time", type=float, default=1.0, help="抽取哪一秒的畫面來檢查（挑素材確實有內容的時間點）")
    ap.add_argument("--out-dir", default="./alpha_check", help="輸出檢查結果的資料夾")
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pix_fmt = ffprobe_pix_fmt(args.video)
    print(f"pix_fmt = {pix_fmt}  {'(有透明通道)' if 'yuva' in pix_fmt else '(沒有透明通道！四個渲染參數哪裡漏了，見 rules/08)'}")

    frame_png = out_dir / "frame.png"
    extract_frame(args.video, args.frame_time, frame_png)

    corner_alphas = check_corner_alpha(frame_png)
    print(f"四個角落像素的alpha值：{corner_alphas}  (應該接近0＝透明；如果都是255代表背景不透明)")

    black_out = out_dir / "on_black.png"
    white_out = out_dir / "on_white.png"
    composite_on(frame_png, (0, 0, 0), black_out)
    composite_on(frame_png, (255, 255, 255), white_out)
    print(f"合成預覽圖已輸出：{black_out}、{white_out}")
    print("兩張都要親眼看過——很多在黑底看起來乾淨的光暈，疊到白底才會顯出不夠白/不夠不透明的髒感。")

    if "yuva" not in pix_fmt:
        sys.exit(1)


if __name__ == "__main__":
    main()
