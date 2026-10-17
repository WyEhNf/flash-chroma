"""从已冻结候选证书绘制缺口与最坏1%均值的后验取舍，不执行模型。"""
import argparse
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix(".json").exists():raise ValueError("不覆盖既有取舍图")
    data = json.loads(args.input.read_text(encoding="utf-8"))
    plt.rcParams.update({"font.family":"Microsoft YaHei","axes.unicode_minus":False,"font.size":10})
    fig,ax = plt.subplots(figsize=(10,5.5),constrained_layout=True)
    for size,marker in ((1,"o"),(2,"s"),(3,"^")):
        rows = [r for r in data["candidates"] if len(r["nodes"]) == size]
        ax.scatter([r["loss"] for r in rows],[(r["tail_mean_delta_lower"]+r["tail_mean_delta_upper"])/2 for r in rows],
            marker=marker,alpha=.65,label=f"{size}节点可行候选",s=35)
    ax.axhline(0,color="black",linewidth=.8,linestyle="--")
    for row,color,marker,label,offset in ((data["selected"],"crimson","*","本轮选择：1582",(14,-6)),
            (data["best_saved_candidate_with_nonincrease_proof"],"teal","D","后验候选：1585",(15,-30))):
        if row is None:continue
        y = (row["tail_mean_delta_lower"]+row["tail_mean_delta_upper"])/2
        ax.scatter([row["loss"]],[y],s=150,color=color,marker=marker,zorder=5)
        ax.annotate(label,(row["loss"],y),xytext=offset,textcoords="offset points",color=color,
            arrowprops={"arrowstyle":"-","color":color})
    ax.set(title="同一批已测候选：尾部缺口与最坏1%均值的取舍",
        xlabel="历史阈值尾部整数缺口（越低越好，非色差单位）",ylabel="完整色域最坏1%均值变化（RGB欧氏码值）")
    ax.ticklabel_format(style="sci",axis="y",scilimits=(0,0))
    ax.grid(alpha=.15)
    ax.legend(loc="lower left")
    fig.savefig(args.output,dpi=160)
    plt.close(fig)
    metadata = {"input_sha256":hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"matplotlib":matplotlib.__version__,
        "candidate_count":len(data["candidates"]),"scope":"仅可视化已保存72候选，纵轴取独立整数区间中点；后验候选未完成100图/原生终验；无新拟合或扫描"}
    args.output.with_suffix(".json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("已生成候选取舍图")


if __name__ == "__main__":main()
