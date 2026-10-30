"""从冻结的分模块源码重建 final1；默认只检查，不覆盖交付文件。"""
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "experiments/final1"
DELIVERY = ROOT / "submission/final1"


def generate():
    seen = set()
    search = [SOURCES, SOURCES / "prefix_joint", SOURCES / "common/framework", SOURCES / "common/include"]

    def expand(path):
        path = path.resolve()
        if path in seen:
            return "// 已在前文内嵌：" + path.name + "\n"
        seen.add(path)
        source = path.read_text(encoding="utf-8-sig")

        def nested(match):
            for folder in [path.parent] + search:
                child = folder / match.group(1)
                if child.is_file():
                    return expand(child)
            raise RuntimeError("缺少本地头文件：" + match.group(1))

        return "// 来源：" + path.name + "\n" + re.sub(
            r'^\s*#\s*include\s+"([^"]+)"\s*$', nested, source, flags=re.M
        )

    header = expand(SOURCES / "final_pipeline.hpp")
    main = (SOURCES / "base_main.cpp").read_text(encoding="utf-8-sig")
    replacements = [
        ("lut_sparse(luts_raw[i], 17,  lut17[i])", "lut_sparse(luts_raw[i], 33,  lut17[i])"),
        ('std::string data_dir = "../data";', 'std::string data_dir = "data";'),
        ("if (argc >= 2) data_dir = argv[1];", "if (argc >= 2) data_dir = argv[1];\n    const int image_count = argc >= 3 ? std::atoi(argv[2]) : 4;\n    if (image_count < 1 || image_count > MAX_IMAGES) return 1;"),
        ("for (int i = 1; i <= 4; i++) {", "for (int i = 1; i <= image_count; i++) {"),
    ]
    for before, after in replacements:
        if main.count(before) != 1:
            raise RuntimeError("原入口不符合冻结版本：" + before)
        main = main.replace(before, after)
    return {"main.cpp": main.encode("utf-8"), "flash_chroma_framework.hpp": header.encode("utf-8")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="写入一个尚不存在的新目录；省略时只检查已提交交付文件")
    args = parser.parse_args()
    files = generate()
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        for name, content in files.items():
            (args.output / name).write_bytes(content)
    else:
        for name, content in files.items():
            if (DELIVERY / name).read_bytes() != content:
                raise RuntimeError("生成结果与冻结交付不一致：" + name)
    print(json.dumps({"complete": True, "files": {name: hashlib.sha256(content).hexdigest() for name, content in files.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
