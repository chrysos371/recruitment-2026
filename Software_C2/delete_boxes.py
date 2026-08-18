"""
Software_C2 — 批量删除误检框 (配合 contact_sheet 使用)
========================================================
扫完缩略图后, 把误检框的编号传给本脚本, 自动从 label 文件删除。

用法:
  python delete_boxes.py 5 17 42 100           # 删除这几个编号的框
  python delete_boxes.py --file to_delete.txt  # 从文件读编号 (每行一个, 可含注释)

说明:
  编号对应 contact_sheet/mapping.csv 里的 idx 列。
  删除后统计剩余各类数量。
"""

import csv
import sys
from pathlib import Path
from collections import Counter

BASE = Path(__file__).parent
MAP_PATH = BASE / "contact_sheet" / "mapping.csv"


def load_mapping():
    m = {}
    with open(MAP_PATH, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            m[int(row["idx"])] = (row["split"], row["image"], int(row["box_idx"]),
                                  int(row["class"]))
    return m


def parse_args():
    idxs = []
    if "--file" in sys.argv:
        fp = sys.argv[sys.argv.index("--file") + 1]
        with open(fp, encoding='utf-8') as f:
            for ln in f:
                ln = ln.split("#")[0].strip()
                if not ln:
                    continue
                for tok in ln.replace(",", " ").split():
                    idxs.append(int(tok))
    else:
        for a in sys.argv[1:]:
            idxs.append(int(a))
    return idxs


def main():
    mapping = load_mapping()
    to_delete = parse_args()
    if not to_delete:
        print("未指定要删除的编号。用法: python delete_boxes.py 5 17 42 ...")
        return

    to_delete = sorted(set(to_delete))
    bad = [i for i in to_delete if i not in mapping]
    if bad:
        print(f"[警告] 以下编号不存在, 已跳过: {bad}")

    # 按 (split, image) 分组要删除的 box_idx
    del_by_img = {}
    for i in to_delete:
        if i not in mapping:
            continue
        split, img, box_idx, cls = mapping[i]
        del_by_img.setdefault((split, img), set()).add(box_idx)

    # 逐图重写 label
    for (split, img), box_idxs in del_by_img.items():
        lab_path = BASE / "dataset" / "labels" / split / f"{img}.txt"
        lines = open(lab_path, encoding='utf-8').read().splitlines()
        keep = [ln for j, ln in enumerate(lines) if j not in box_idxs]
        with open(lab_path, "w", encoding='utf-8') as f:
            f.write("\n".join(keep) + ("\n" if keep else ""))
        print(f"  {split}/{img}: 删除 {len(box_idxs)} 框")

    # 统计剩余
    cnt = Counter()
    for split in ["train", "val"]:
        for lf in (BASE / "dataset" / "labels" / split).glob("*.txt"):
            for ln in open(lf, encoding='utf-8'):
                ln = ln.strip()
                if ln:
                    cnt[int(ln.split()[0])] += 1
    print(f"\n删除完成。剩余框分布: "
          f"community={cnt[0]}  non_comm={cnt[1]}  bike={cnt[2]}  总={sum(cnt.values())}")


if __name__ == "__main__":
    main()
