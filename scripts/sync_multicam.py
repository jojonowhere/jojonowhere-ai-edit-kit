#!/usr/bin/env python3
"""多機位（例如臉部鏡頭＋螢幕錄影）音訊比對同步：抓出隨時間變化的偏移量，不是單一固定秒差。

背景：兩支獨立裝置就算同時開始錄，時間軸也不會完全對齊——不只是固定秒差，兩台裝置內部
時鐘走速本身有微小差異，短片段感覺不出來，但拉到超過一小時的長素材會累積成看得出來的偏移，
且偏移量隨時間變化。只用單一固定秒差對齊，在長素材上會失敗（同一次錄影裡不同剪點需要的
修正幀數可能差到7-8幀）。

做法：在兩支素材裡選3個以上時間點（開頭、中間、結尾附近），各自用音訊交叉相關算出當下
真實偏移秒數，再用這些(時間點,偏移量)擬合一條線性迴歸，得到隨時間變化的偏移量函式。

用法：
    python3 sync_multicam.py ref.mov other.mov --points 0 1800 3600
    # --points 是要在ref素材上取樣比對的時間點（秒），至少給3個，涵蓋開頭/中段/尾段
"""
import argparse

import librosa
import numpy as np
from scipy.signal import correlate


def load_audio_window(path, center_sec, window_sec, sr):
    offset = max(0, center_sec - window_sec / 2)
    y, _ = librosa.load(path, sr=sr, offset=offset, duration=window_sec, mono=True)
    return y


def find_offset_seconds(ref_audio, other_audio, sr, search_window_sec):
    corr = correlate(other_audio, ref_audio, mode="full")
    lag = np.argmax(corr) - (len(ref_audio) - 1)
    offset_sec = lag / sr
    if abs(offset_sec) > search_window_sec:
        print(f"    警告：算出的偏移量 {offset_sec:.3f}s 超過取樣視窗，結果可能不可靠")
    return offset_sec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref", help="基準素材（例如臉部鏡頭）")
    ap.add_argument("other", help="要對齊到基準的素材（例如螢幕錄影）")
    ap.add_argument("--points", type=float, nargs="+", required=True,
                     help="在ref素材上取樣比對的時間點（秒），至少3個，建議涵蓋開頭/中段/尾段")
    ap.add_argument("--window", type=float, default=20.0, help="每個取樣點抓多長的音訊窗口做比對（秒）")
    ap.add_argument("--sr", type=int, default=22050, help="分析用的取樣率")
    args = ap.parse_args()

    if len(args.points) < 3:
        print("警告：少於3個取樣點，線性迴歸的漂移估計會不可靠，建議至少3個涵蓋開頭/中段/尾段", flush=True)

    measured = []
    for t in args.points:
        print(f"取樣 t={t:.1f}s ...")
        ref_audio = load_audio_window(args.ref, t, args.window, args.sr)
        other_audio = load_audio_window(args.other, t, args.window, args.sr)
        offset = find_offset_seconds(ref_audio, other_audio, args.sr, args.window)
        measured.append((t, offset))
        print(f"    偏移量 = {offset:+.4f}s")

    ts = np.array([p[0] for p in measured])
    offsets = np.array([p[1] for p in measured])
    slope, intercept = np.polyfit(ts, offsets, 1)

    print("\n擬合結果：offset(t) = slope * t + intercept")
    print(f"  slope     = {slope:.8f}  (每秒漂移量)")
    print(f"  intercept = {intercept:+.4f}s")

    t_min, t_max = ts.min(), ts.max()
    drift = (slope * t_max + intercept) - (slope * t_min + intercept)
    print(f"\n從 t={t_min:.0f}s 到 t={t_max:.0f}s 累積漂移 {drift:+.3f}s")
    print("\n套用方式：other素材上任一時間點t，對齊到ref時間軸要加的偏移量＝slope*t+intercept")
    print("不要對整支素材套同一個固定offset，每個剪點都要代入它自己的時間點算當下偏移量。")


if __name__ == "__main__":
    main()
