#!/usr/bin/env python3
"""從Premiere .prproj檔案抓出已剪輯序列的EDL（每段clip的軌道/檔名/時間碼），輸出成JSON。

背景：.prproj是gzip壓縮的XML，內部用ObjectID/ObjectRef/ObjectURef這種物件圖譜的方式
互相參照（不是巢狀結構），要先把所有帶ObjectID的節點收成一張表，再用ObjectRef/ObjectURef
的值去表裡查對應節點。這個格式沒有單一可靠的官方規格，不同Premiere版本XML細節可能有出入
（實測環境：Premiere Pro 2026 26.2.0），如果某個Sequence解不出clip，先用
`--dump-tags`看實際XML用了哪些標籤名稱，再調整下面SEQUENCE_TAG/CLIPITEM_TAG等常數。

時間單位：Premiere內部用「ticks」，換算常數 254016000000 ticks/秒，是實測驗證過的值。

用法：
    python3 parse_prproj.py 專案.prproj --sequence "Sequence 01" -o edl.json
    python3 parse_prproj.py 專案.prproj --dump-tags   # 先看XML裡有哪些標籤，抓不到東西時用
"""
import argparse
import gzip
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter

TICKS_PER_SECOND = 254016000000

SEQUENCE_TAG = "Sequence"
TRACK_TAG = "Track"
CLIPITEM_TAG = "ClipItem"
NAME_TAG = "Name"


def load_xml(path):
    with open(path, "rb") as f:
        head = f.read(2)
    with open(path, "rb") as f:
        raw = f.read()
    if head == b"\x1f\x8b":
        raw = gzip.decompress(raw)
    return ET.fromstring(raw)


def build_id_index(root):
    """收集所有帶ObjectID屬性的節點，回傳 {ObjectID: Element}。"""
    index = {}
    for el in root.iter():
        obj_id = el.get("ObjectID") or el.get("ObjectUID")
        if obj_id:
            index[obj_id] = el
    return index


def resolve_ref(el, index):
    """跟著ObjectRef/ObjectURef子節點的文字值去id_index裡查出實際節點，查不到回傳None。"""
    for tag in ("ObjectRef", "ObjectURef"):
        ref_el = el.find(tag)
        if ref_el is not None and ref_el.text:
            return index.get(ref_el.text.strip())
    return None


def dump_tags(root):
    counter = Counter(el.tag for el in root.iter())
    for tag, count in counter.most_common(60):
        print(f"{count:6d}  {tag}")


def find_name(el, index):
    name_el = el.find(NAME_TAG)
    if name_el is not None and name_el.text:
        return name_el.text
    ref = resolve_ref(el, index)
    if ref is not None:
        name_el = ref.find(NAME_TAG)
        if name_el is not None and name_el.text:
            return name_el.text
    return None


def ticks_to_seconds(value):
    try:
        return int(value) / TICKS_PER_SECOND
    except (TypeError, ValueError):
        return None


def extract_clips(sequence_el, index):
    clips = []
    for track_idx, track_el in enumerate(sequence_el.iter(TRACK_TAG)):
        for clip_el in track_el.findall(CLIPITEM_TAG):
            start = ticks_to_seconds(clip_el.get("Start") or (clip_el.find("Start").text if clip_el.find("Start") is not None else None))
            end = ticks_to_seconds(clip_el.get("End") or (clip_el.find("End").text if clip_el.find("End") is not None else None))
            in_pt = ticks_to_seconds(clip_el.get("InPoint") or (clip_el.find("InPoint").text if clip_el.find("InPoint") is not None else None))
            out_pt = ticks_to_seconds(clip_el.get("OutPoint") or (clip_el.find("OutPoint").text if clip_el.find("OutPoint") is not None else None))
            clips.append({
                "track": track_idx,
                "name": find_name(clip_el, index),
                "start_sec": start,
                "end_sec": end,
                "in_sec": in_pt,
                "out_sec": out_pt,
            })
    clips.sort(key=lambda c: (c["track"], c["start_sec"] if c["start_sec"] is not None else 0))
    return clips


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prproj", help=".prproj檔案路徑")
    ap.add_argument("--sequence", help="要抓的Sequence名稱（不指定就抓第一個找到的）")
    ap.add_argument("-o", "--output", help="輸出JSON路徑，不指定就印到stdout")
    ap.add_argument("--dump-tags", action="store_true", help="不解析，只列出XML裡出現過的標籤名稱與次數（schema對不上時先用這個看）")
    args = ap.parse_args()

    root = load_xml(args.prproj)

    if args.dump_tags:
        dump_tags(root)
        return

    index = build_id_index(root)

    sequences = list(root.iter(SEQUENCE_TAG))
    if not sequences:
        print(f"沒有找到任何 <{SEQUENCE_TAG}> 節點，先跑 --dump-tags 確認實際標籤名稱", file=sys.stderr)
        sys.exit(1)

    target = None
    if args.sequence:
        for seq in sequences:
            if find_name(seq, index) == args.sequence:
                target = seq
                break
        if target is None:
            print(f"找不到名稱為「{args.sequence}」的Sequence，可用名稱：", file=sys.stderr)
            for seq in sequences:
                print(f"  - {find_name(seq, index)}", file=sys.stderr)
            sys.exit(1)
    else:
        target = sequences[0]

    clips = extract_clips(target, index)
    output = json.dumps(clips, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"寫出 {len(clips)} 個clip -> {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
