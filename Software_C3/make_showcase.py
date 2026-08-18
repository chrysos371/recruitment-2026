"""
Software_C3 — 生成精简展示集
================================
从无干扰原始图 + 干扰增强图中, 各挑 4 种状态 (红/黄/绿/熄灭) 的代表性
检测结果图, 输出到 展示/无干扰/ 与 展示/干扰/, 满足题目
"无干扰环境下四种状态展示 + 干扰环境下的四种状态展示" 的要求。
"""

import os
import numpy as np
from pathlib import Path

import traffic_light_detector as tld
import augment_and_test as aug


def pick_best(base_dir, images, rng):
    """对每个状态挑置信度最高的一张, 返回 {state: img_array}。"""
    best = {"red": (None, -1), "yellow": (None, -1),
            "green": (None, -1), "off": (None, -1)}
    for f in images:
        img = aug.read_img(f)
        res = tld.detect_lights_array(img)
        st = res["state"]
        conf = max((b[5] for b in res["boxes"]), default=0)
        if st in best and conf > best[st][1]:
            best[st] = (img, conf)
    return {k: v[0] for k, v in best.items() if v[0] is not None}


def save_annotated(img, dst):
    res = tld.detect_lights_array(img)
    ann = tld.draw_result(img, res)
    aug.save_img(ann, dst)


def main():
    base = Path(__file__).parent
    rng = np.random.default_rng(42)
    showcase = base / "展示"
    clean_dir = showcase / "无干扰"
    dist_dir = showcase / "干扰"
    clean_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    clean_imgs = sorted(base.glob("*.jpg"))
    state_name = {"red": "红灯", "yellow": "黄灯", "green": "绿灯", "off": "熄灭"}

    # ---------- 无干扰: 原始图里挑红/黄/绿, 再用 aug_off 生成熄灭 ----------
    best = pick_best(base, clean_imgs, rng)
    for st in ["red", "yellow", "green"]:
        if st in best:
            save_annotated(best[st], clean_dir / f"{state_name[st]}_{st}.jpg")

    # 熄灭: 对一张亮灯图做熄灯增强 (无其他干扰)
    src = best.get("green")
    if src is None:
        src = best.get("red")
    if src is None:
        src = best.get("yellow")
    if src is not None:
        off_img = aug.aug_off(src, rng)
        save_annotated(off_img, clean_dir / f"{state_name['off']}_off.jpg")

    # ---------- 干扰: 从增强图里挑红/黄/绿/熄灭 ----------
    dist_imgs = sorted((base / "disturbed").glob("*.jpg"))
    best_dist = pick_best(base, dist_imgs, rng)
    for st in ["red", "yellow", "green", "off"]:
        if st in best_dist:
            save_annotated(best_dist[st], dist_dir / f"{state_name[st]}_{st}.jpg")

    # ---------- 汇总 ----------
    print("=" * 50)
    print("  展示集生成完成:")
    print("=" * 50)
    for d in [clean_dir, dist_dir]:
        print(f"\n  {d.relative_to(base)}/")
        for f in sorted(d.glob("*.jpg")):
            print(f"    {f.name}")

    print(f"\n  共 {len(list(clean_dir.glob('*.jpg')))} + "
          f"{len(list(dist_dir.glob('*.jpg')))} 张展示图")


if __name__ == "__main__":
    main()
