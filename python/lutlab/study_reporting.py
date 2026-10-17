"""由冻结测量派生报告，显式绑定基线容量。"""


def select_baseline(rows, size=33):
    matches = [row for row in rows if row["profile"] == "sample_tetra"
               and int(row["m"]) == size]
    if len(matches) != 1:
        raise ValueError(f"报告要求唯一 sample_tetra/m{size} 基线，实际找到 {len(matches)} 条")
    return matches[0]
