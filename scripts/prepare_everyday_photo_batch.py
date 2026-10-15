"""Build the reviewed everyday-photo set from two separately downloaded archives.

Run from the repository root with Pillow installed. No archive is extracted to
arbitrary filesystem paths. Downloads and original archives stay outside Git.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
from pathlib import Path
import platform
import tarfile
import zipfile

from PIL import Image, ImageDraw, ImageOps, __version__ as PILLOW_VERSION

ROOT = Path(__file__).resolve().parents[1]
PHOTOS = ROOT / "assets/photos"
DPED_URL = "https://download.ai-benchmark.com/s/9RqJ5JZPDggMoyo/download/sample_images.gz"
DIV2K_URL = "https://data.vision.ee.ethz.ch/cvl/DIV2K/DIV2K_valid_HR.zip"
# Reviewed on contact sheets; exclude specialized, strongly stylized or repeated
# subject examples to favour ordinary photographs. This is a curated subset.
EXCLUDED_DIV2K = {809, 819, 821, 828, 838, 839, 840, 852, 856, 858,
                  859, 863, 866, 870, 874, 886, 893, 895, 896}
DPED_IDS = [34, 41, 47, 50, 55, 56, 60, 68, 83, 85, 92, 95, 98, 107]
DIV2K_SCENES = {
    "animals": [801, 805, 810, 829, 842, 862, 869, 880, 882],
    "people": [804, 813, 817, 825, 832, 844, 855, 860, 888, 894],
    "food_and_shopping": [802, 822, 831, 833, 837, 848, 867, 871, 872, 875, 889],
    "plants_and_nature": [803, 815, 843, 849, 853, 857, 877, 897, 898, 899],
    "landscape_and_travel": [806, 807, 808, 811, 823, 835, 876],
    "city_and_architecture": [812, 814, 816, 818, 820, 824, 826, 827, 830, 834,
                              836, 841, 845, 846, 847, 850, 851, 854, 861, 864,
                              865, 868, 873, 878, 879, 881, 883, 884, 885, 887,
                              890, 891, 892, 900],
}


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def archive_sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def process(payload: bytes, destination: Path) -> dict:
    with Image.open(BytesIO(payload)) as source:
        source.load()
        original = {"sha256": sha(payload), "bytes": len(payload),
                    "size": list(source.size), "mode": source.mode, "format": source.format}
        frame = ImageOps.exif_transpose(source)
        if frame.height > frame.width:
            frame = frame.rotate(90, expand=True)
        frame = frame.convert("RGB").resize((1024, 768), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Compression changes file size only, never the RGB8 pixel values.
        frame.save(destination, format="PNG", compress_level=9)
    return {"original": original, "evaluation": {
        "path": destination.relative_to(ROOT).as_posix(), "size": [1024, 768],
        "mode": "RGB", "bytes": destination.stat().st_size,
        "sha256": sha(destination.read_bytes()), "pixel_sha256": sha(frame.tobytes())}}


def write_previews(records: list[dict]) -> None:
    previews = PHOTOS / "previews"
    previews.mkdir(exist_ok=True)
    for page in range(4):
        sheet = Image.new("RGB", (1280, 1080), "white")
        draw = ImageDraw.Draw(sheet)
        for index, record in enumerate(records[page * 25:(page + 1) * 25]):
            x, y = index % 5 * 256, index // 5 * 216
            with Image.open(ROOT / record["evaluation"]["path"]) as frame:
                sheet.paste(frame.resize((256, 192), Image.Resampling.LANCZOS), (x, y))
            draw.text((x + 4, y + 196), record["id"], fill="black")
        sheet.save(previews / f"sheet-{page + 1:02d}.jpg", quality=85)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dped", type=Path, required=True)
    parser.add_argument("--div2k", type=Path, required=True)
    args = parser.parse_args()
    scene_lookup = {number: scene for scene, numbers in DIV2K_SCENES.items() for number in numbers}
    selected = sorted(set(range(801, 901)) - EXCLUDED_DIV2K)
    assert len(selected) == 81 and set(scene_lookup) == set(selected)
    records = []
    old = json.loads((PHOTOS / "kodak/manifest.json").read_text(encoding="utf-8"))
    for row in old["images"]:
        record = dict(row, dataset="kodak", id="kodak-" + row["id"])
        with Image.open(ROOT / row["evaluation"]["path"]) as frame:
            record["evaluation"] = dict(row["evaluation"], mode=frame.mode,
                                        pixel_sha256=sha(frame.tobytes()))
        records.append(record)
    with tarfile.open(args.dped, "r:*") as archive:
        for number in DPED_IDS:
            member = f"sample_images/original_images/sony/{number}.jpg"
            with archive.extractfile(member) as source:
                record = process(source.read(), PHOTOS / f"dped/rgb8-1024x768/sony-{number:03d}.png")
            record.update(id=f"dped-sony-{number:03d}", dataset="dped", scene="everyday_phone_street_and_landscape",
                          source_page="https://aiff22.github.io/", archive_member=member,
                          source_url=DPED_URL, device="Sony Xperia Z")
            records.append(record)
    with zipfile.ZipFile(args.div2k) as archive:
        for number in selected:
            member = f"DIV2K_valid_HR/{number:04d}.png"
            record = process(archive.read(member), PHOTOS / f"div2k/rgb8-1024x768/{number:04d}.png")
            record.update(id=f"div2k-{number:04d}", dataset="div2k", scene=scene_lookup[number],
                          source_page="https://data.vision.ee.ethz.ch/cvl/DIV2K/", archive_member=member,
                          source_url=DIV2K_URL, split="validation")
            records.append(record)
    assert len(records) == 100
    paths = [r["evaluation"]["path"] for r in records]
    assert len(set(paths)) == len(set(r["evaluation"]["pixel_sha256"] for r in records)) == 100
    manifest = {
        "schema_version": 1, "created_utc": datetime.now(timezone.utc).isoformat(),
        "generator": {"path": "scripts/prepare_everyday_photo_batch.py",
                      "sha256": sha(Path(__file__).read_bytes()),
                      "python": platform.python_version(), "pillow": PILLOW_VERSION},
        "count": 100, "dataset_counts": {"kodak": 5, "dped": 14, "div2k": 81},
        "curation": "Contact-sheet review; one Sony image per DPED scene; 19 specialized/strongly stylized/repeated-subject DIV2K examples excluded. No claim of balanced coverage or statistical independence.",
        "transform": "EXIF transpose; rotate portrait 90 degrees; RGB; Lanczos resize to 1024x768; no tone/exposure/color edits. Aspect ratios may change, matching lutlab.data._to_frame.",
        "source_archives": {
            "dped": {"url": DPED_URL, "bytes": args.dped.stat().st_size, "sha256": archive_sha(args.dped)},
            "div2k": {"url": DIV2K_URL, "bytes": args.div2k.stat().st_size, "sha256": archive_sha(args.div2k)}},
        "rights": {
            "kodak": old["rights_note"],
            "dped": "Public research dataset distributed by the authors; retain source and paper attribution. No new license grant is asserted here.",
            "div2k": "Official dataset page: academic research purpose only; image copyright belongs to the original owners. This subset inherits those restrictions, not the repository code license."},
        "original_storage": "Only existing Kodak originals are versioned. DPED/DIV2K original archives remain local; member names and original byte hashes support retrieval.",
        "images": records,
    }
    (PHOTOS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PHOTOS / "eval.txt").write_text("".join(path + "\n" for path in paths), encoding="utf-8")
    write_previews(records)
    print(json.dumps({"count": len(records), "dataset_counts": manifest["dataset_counts"],
                      "evaluation_bytes": sum(r["evaluation"]["bytes"] for r in records)}, indent=2))


if __name__ == "__main__":
    main()
