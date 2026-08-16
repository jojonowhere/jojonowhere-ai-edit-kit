#!/usr/bin/env python3
"""逐幀數位變焦：對一段已抽成PNG序列的畫面做「持平→推近→持平→拉遠」的裁切+放大回原尺寸。

用ffmpeg的crop filter做不到這件事——它的w/h雖然標示支援time-varying表達式，
實測並不會真的逐幀重新套用（"T"旗標會誤導），所以改用PIL逐幀處理再用ffmpeg組回影片。

用法：
    1. 先抽幀：ffmpeg -i 來源.mov -vf fps=30 frames/f_%05d.png
    2. 跑這支腳本產生裁切後的frames
    3. 組回影片：ffmpeg -framerate 30 -i out_frames/f_%05d.png -c:v prores_ks ... out.mov
"""
import argparse
import glob
import os

from PIL import Image


def ease_in_out_hold(t, t_hold_start, t_ease_in_end, t_hold_end, t_ease_out_end):
    """回傳0~1的推進比例p：0=完全沒推近(原始畫面)，1=推到最緊(zoom target)。

    四段式包絡：[0,hold_start]持平在0 → 線性推進到1 → 持平在1 → 線性拉回到0。
    """
    if t < t_hold_start:
        return 0.0
    if t < t_ease_in_end:
        return (t - t_hold_start) / (t_ease_in_end - t_hold_start)
    if t < t_hold_end:
        return 1.0
    if t < t_ease_out_end:
        return 1.0 - (t - t_hold_end) / (t_ease_out_end - t_hold_end)
    return 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src_dir", help="抽好的PNG序列來源資料夾")
    ap.add_argument("dst_dir", help="裁切後輸出的PNG序列資料夾（要先存在）")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--full-w", type=int, required=True, help="原始畫面寬度")
    ap.add_argument("--full-h", type=int, required=True, help="原始畫面高度")
    ap.add_argument("--tight-h", type=float, required=True, help="推到最緊時的裁切高度（寬度依原始長寬比自動算）")
    ap.add_argument("--center-x", type=float, default=None, help="裁切水平中心，預設全畫面正中央")
    ap.add_argument("--pan-y", type=float, default=0.0, help="推近時裁切框往下平移的最大距離（px），0＝只放大不平移")
    ap.add_argument("--hold-start", type=float, default=0.0, help="開始推近的時間點（秒）")
    ap.add_argument("--ease-in-end", type=float, required=True, help="推到最緊的時間點（秒）")
    ap.add_argument("--hold-end", type=float, required=True, help="開始拉遠的時間點（秒）")
    ap.add_argument("--ease-out-end", type=float, required=True, help="拉回原始畫面的時間點（秒）")
    args = ap.parse_args()

    full_w, full_h = args.full_w, args.full_h
    tight_h = args.tight_h
    tight_w = tight_h * (full_w / full_h)
    center_x = args.center_x if args.center_x is not None else full_w / 2

    files = sorted(glob.glob(os.path.join(args.src_dir, "*.png")))
    if not files:
        raise SystemExit(f"沒有在 {args.src_dir} 找到任何 .png 檔")

    for idx, f in enumerate(files):
        t = idx / args.fps
        p = ease_in_out_hold(t, args.hold_start, args.ease_in_end, args.hold_end, args.ease_out_end)
        h = full_h - p * (full_h - tight_h)
        w = h * (full_w / full_h)
        x = center_x - w / 2
        y = p * args.pan_y

        im = Image.open(f)
        box = (round(x), round(y), round(x + w), round(y + h))
        cropped = im.crop(box)
        resized = cropped.resize((full_w, full_h), Image.LANCZOS)
        resized.save(os.path.join(args.dst_dir, os.path.basename(f)))

    print(f"done: {len(files)} frames -> {args.dst_dir}")


if __name__ == "__main__":
    main()
