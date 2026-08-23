#!/usr/bin/env python3
"""把一張靜態圖片（照片/截圖）做成「懸浮光暈卡片」風格的透明PNG：縮圖裝進細白邊圓角卡片，
疊多層漸層光暈＋陰影，卡片本身帶一點隨手擺放的傾斜角度，輸出透明背景PNG可以直接貼進任何畫面。

這是rules/07-懸浮光暈卡片視覺規範.md規範的「靜態圖片版」實作（動態素材走Remotion管線，見
rules/08）。所有預設參數都是2026-08-24反覆調整、實測驗證過的數值，不要沒理由亂改。

用法：
    python3 scripts/floating_glow_card.py 來源圖片.png 輸出.png
    python3 scripts/floating_glow_card.py 來源圖片.png 輸出.png --rotate 0   # 不要傾斜角度
    python3 scripts/floating_glow_card.py 來源圖片.png 輸出.png --width 1600
"""
import argparse

from PIL import Image, ImageDraw, ImageFilter


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def light_blob(canvas_size, card_size, scale_w, scale_h, blur, alpha):
    cw, ch = canvas_size
    card_w, card_h = card_size
    bw, bh = round(card_w * scale_w), round(card_h * scale_h)
    shape = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    blob = Image.new("RGBA", (bw, bh), (255, 255, 255, 255))
    blob.putalpha(rounded_mask((bw, bh), min(bw, bh) // 2))
    x, y = (cw - bw) // 2, (ch - bh) // 2
    shape.paste(blob, (x, y), blob)
    shape = shape.filter(ImageFilter.GaussianBlur(blur))
    r, g, b, a = shape.split()
    return Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * alpha))))


def verify_edge_clean(canvas, band=40):
    """檢查邊界一整條帶的alpha，不是只看最外面那一像素——見rules/07的「已知會踩的坑」，
    只驗證單一像素會漏掉「還沒完全模糊完就被裁切」的殘留硬邊。"""
    px = canvas.load()
    w, h = canvas.size
    max_alpha = 0
    for y in range(band):
        for x in range(0, w, max(1, w // 200)):
            max_alpha = max(max_alpha, px[x, y][3], px[x, h - 1 - y][3])
    for x in range(band):
        for y in range(0, h, max(1, h // 200)):
            max_alpha = max(max_alpha, px[x, y][3], px[w - 1 - x, y][3])
    return max_alpha


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="來源圖片路徑")
    ap.add_argument("out", help="輸出PNG路徑（透明背景）")
    ap.add_argument("--width", type=int, default=1100, help="卡片內容縮放到的寬度（預設1100px）")
    ap.add_argument("--rotate", type=float, default=-4.5, help="卡片傾斜角度，預設-4.5度，設0關閉")
    ap.add_argument("--glow-strength", type=float, default=1.0,
                     help="光暈整體強度倍率，預設1.0＝目前定案的2/3強度版本，太重了再往下調")
    args = ap.parse_args()

    img = Image.open(args.src).convert("RGBA")
    scale = args.width / img.width
    img = img.resize((args.width, round(img.height * scale)), Image.LANCZOS)
    W, H = img.size

    photo_radius = round(W * 0.045)
    margin = round(W * 0.012)  # 細白邊，不要加大——加大會變成「相框感」蓋過「發光感」
    card_radius = photo_radius + margin

    photo_mask = rounded_mask((W, H), photo_radius)
    photo_rounded = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    photo_rounded.paste(img, (0, 0), photo_mask)

    card_w, card_h = W + margin * 2, H + margin * 2
    card_mask = rounded_mask((card_w, card_h), card_radius)
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    white_bg = Image.new("RGBA", (card_w, card_h), (255, 255, 255, 255))
    card.paste(white_bg, (0, 0), card_mask)
    card.paste(photo_rounded, (margin, margin), photo_rounded)

    # 0.95×W：面積抓半個畫布（邊長×√2/2），2026-08-24校正值——夠讓最寬那層光暈在
    # 模糊前先完整落在畫布裡，模糊才有空間收斂到0，不會被邊界硬切出一圈殘留邊
    pad = round(W * 0.95)
    cw, ch = card_w + pad * 2, card_h + pad * 2
    canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))

    # 四層堆疊：緊亮核心→中層→寬層→柔和外擴，不要用單一模糊（單層只會做出「霧感」不是「光感」）
    glow_layers = [
        (1.05, 1.10, round(W * 0.025), 0.98),
        (1.30, 1.35, round(W * 0.06), 0.75),
        (1.60, 1.65, round(W * 0.14), 0.45),
        (1.90, 2.00, round(W * 0.24), 0.20),
    ]
    reduce = (2 / 3) * args.glow_strength
    for s_w, s_h, blur, alpha in glow_layers:
        canvas = Image.alpha_composite(canvas, light_blob((cw, ch), (card_w, card_h), s_w, s_h, blur, alpha * reduce))

    shadow = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    shadow_solid = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 255))
    shadow_solid.putalpha(card_mask)
    sx, sy = (cw - card_w) // 2, (ch - card_h) // 2
    shadow.paste(shadow_solid, (sx, sy + round(W * 0.018)), shadow_solid)
    shadow = shadow.filter(ImageFilter.GaussianBlur(round(W * 0.025)))
    r, g, b, a = shadow.split()
    shadow = Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * 0.30))))
    canvas = Image.alpha_composite(canvas, shadow)

    canvas.paste(card, (sx, sy), card)

    if args.rotate:
        canvas = canvas.rotate(args.rotate, resample=Image.BICUBIC, expand=True)

    max_edge_alpha = verify_edge_clean(canvas)
    if max_edge_alpha > 2:
        print(f"警告：邊界40px範圍內偵測到殘留alpha={max_edge_alpha}（應該接近0），"
              f"代表pad不夠、光暈被畫布邊界裁切了，考慮調大pad", flush=True)
    else:
        print(f"邊界檢查通過（max alpha={max_edge_alpha}）")

    canvas.save(args.out)
    print(f"saved {args.out} {canvas.size}")


if __name__ == "__main__":
    main()
