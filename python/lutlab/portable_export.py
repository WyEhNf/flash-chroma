"""Export four provenance-verified tetrahedral models as const C99 ROM arrays.

The development host needs Python. The generated firmware bundle needs only the
portable C99 runtime and the target C compiler. Export never fits, composes or
changes a model, and refuses manifests specifying another interpolation basis.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile

from . import io


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def export_models(paths, destination, *, prefix="flash_chroma"):
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,47}", prefix):
        raise ValueError("C symbol prefix must contain 1..48 lowercase letters, digits or underscores, starting with a letter")
    paths = [Path(path).resolve() for path in paths]
    contract = io.inspect_submission_contract(paths, semantics="independent")
    if not contract["pass"] or contract["semantics_evidence"] != "verified_model_manifest":
        raise ValueError("ROM export requires four legal independent models with their verified cache manifest")
    source_manifest = paths[0].parent / "manifest.json"
    manifest_payload = source_manifest.read_bytes()
    manifest = json.loads(manifest_payload)
    parameters = manifest["identity"]["parameters"]
    if parameters.get("interpolation_basis") != "tetra_q16":
        raise ValueError("portable C99 executes tetra_q16 only; the manifest has another or unknown interpolation basis")
    inputs = manifest["identity"]["inputs"]
    if (len(inputs) != 4 or len({item["sha256"] for item in inputs}) != 4
            or parameters.get("semantics") != "independent" or parameters.get("n_stages") != 4):
        raise ValueError("ROM export requires four distinct ordered original-LUT identities and independent stages")
    blobs = [path.read_bytes() for path in paths]
    digests = [sha(blob) for blob in blobs]
    sizes = contract["grid_sizes"]
    destination = Path(destination).resolve()
    if destination.exists():
        raise FileExistsError("preserve the existing ROM bundle; choose a new output directory")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".portable-export-", dir=destination.parent)).resolve()
    try:
        guard = prefix.upper() + "_PORTABLE_MODEL_H"
        declarations = "\n".join(f"extern const uint8_t {prefix}_stage{s+1}[{len(blob)}];" for s, blob in enumerate(blobs))
        header = f"""/* Generated ROM model. Keep portable-model.json as host-side provenance. */
#ifndef {guard}
#define {guard}
#include "jshc_portable.h"
#if JSHC_P_ABI_VERSION != 1u
#error "This ROM bundle requires portable ABI 1"
#endif
#ifdef __cplusplus
extern "C" {{
#endif
{declarations}
extern const uint8_t *const {prefix}_blobs[JSHC_P_STAGES];
extern const size_t {prefix}_blob_bytes[JSHC_P_STAGES];
/* Caller owns models/chain and keeps them alive. Preparation may initialize a
 * prefix of models before reporting an error; it never modifies ROM bytes. */
jshc_p_status {prefix}_prepare(jshc_p_model models[JSHC_P_STAGES],
                             jshc_p_chain *chain, uint32_t options);
#ifdef __cplusplus
}}
#endif
#endif
"""
        source = [f'/* Generated, byte-preserved SLUT v1 / tetra_q16. */\n#include "{prefix}.h"\n']
        for stage, blob in enumerate(blobs, 1):
            source.append(f"/* SHA256 {digests[stage-1]} */\nconst uint8_t {prefix}_stage{stage}[{len(blob)}] = {{\n")
            source.extend("    " + ",".join(f"0x{value:02x}" for value in blob[start:start+16]) + ",\n"
                          for start in range(0, len(blob), 16))
            source.append("};\n")
        source.append(f"const uint8_t *const {prefix}_blobs[JSHC_P_STAGES] = {{ " +
                      ", ".join(f"{prefix}_stage{stage}" for stage in range(1, 5)) + " };\n")
        source.append(f"const size_t {prefix}_blob_bytes[JSHC_P_STAGES] = {{ " +
                      ", ".join(f"{len(blob)}u" for blob in blobs) + " };\n")
        source.append(f"""
jshc_p_status {prefix}_prepare(jshc_p_model models[JSHC_P_STAGES],
                             jshc_p_chain *chain, uint32_t options) {{
    const jshc_p_model *views[JSHC_P_STAGES];
    unsigned stage;
    if (models == NULL || chain == NULL) return JSHC_P_NULL;
    for (stage = 0; stage < JSHC_P_STAGES; ++stage) {{
        jshc_p_status status = jshc_p_model_prepare(&models[stage],
                {prefix}_blobs[stage], {prefix}_blob_bytes[stage]);
        if (status != JSHC_P_OK) return status;
        views[stage] = &models[stage];
    }}
    return jshc_p_chain_prepare(chain, views, options);
}}
""")
        generated = {prefix + ".h": header.encode("utf-8"), prefix + ".c": "".join(source).encode("utf-8"),
                     "model-source-manifest.json": manifest_payload}
        if manifest.get("kind") == "independent_stage_bundle_v1":
            for parent in manifest["identity"]["parents"]:
                name = parent["file"]
                payload = (source_manifest.parent / name).read_bytes()
                if sha(payload) != parent["manifest_sha256"]:
                    raise RuntimeError("bundle parent provenance changed during export")
                generated[name] = payload
        for name, payload in generated.items():
            (temporary / name).parent.mkdir(parents=True, exist_ok=True)
            (temporary / name).write_bytes(payload)
        package = Path(__file__).resolve().parent
        repository = package.parents[1]
        metadata = {"schema": 1, "kind": "portable_const_c99_rom", "prefix": prefix,
                    "portable_abi": 1, "format": "SLUT v1", "interpolation_basis": "tetra_q16",
                    "semantics": "independent", "stage_count": 4, "grid_sizes": sizes,
                    "ordered_source_sha256": [item["sha256"] for item in inputs],
                    "ordered_model_sha256": digests, "ordered_blob_bytes": [len(blob) for blob in blobs],
                    "serialized_rom_payload_bytes": sum(map(len, blobs)),
                    "original_rgb_node_payload_bytes": sum(io.load_sparse(path, competition=True).nodes.nbytes for path in paths),
                    "source_model_identity_sha256": manifest["identity_sha256"], "source_manifest_sha256": sha(manifest_payload),
                    "exporter_sha256": sha(Path(__file__).read_bytes()),
                    "runtime_source_sha256": {name: sha((repository / name).read_bytes()) for name in (
                        "portable/include/jshc_portable.h", "portable/src/jshc_portable.c")},
                    "generated_files": {name: {"bytes": len(payload), "sha256": sha(payload)} for name, payload in generated.items()},
                    "runtime_dependencies": "target C99 compiler and portable runtime; memory helpers supplied by the board/runtime",
                    "workspace": "four caller-owned jshc_p_model objects and one jshc_p_chain; query ABI sizes on the target",
                    "rom_memory_scope": "serialized array payload only; target linker pointer/size tables, code and padding are additional",
                    "quality_scope": "provenance and byte-preserving export only; no new accuracy, hardware speed or official pass claim",
                    "new_fits": 0, "official": False}
        (temporary / "portable-model.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if [sha(path.read_bytes()) for path in paths] != digests or source_manifest.read_bytes() != manifest_payload:
            raise RuntimeError("source model or manifest changed during export")
        temporary.rename(destination)
        return metadata
    finally:
        if temporary.exists():
            if temporary.parent != destination.parent or not temporary.name.startswith(".portable-export-"):
                raise RuntimeError("refusing cleanup outside this export's temporary directory")
            shutil.rmtree(temporary)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs=4, required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--prefix", default="flash_chroma")
    args = parser.parse_args(argv)
    metadata = export_models(args.models, args.output, prefix=args.prefix)
    print(json.dumps({"output": str(args.output.resolve()), "stage_count": metadata["stage_count"],
                      "grid_sizes": metadata["grid_sizes"], "serialized_rom_payload_bytes": metadata["serialized_rom_payload_bytes"],
                      "interpolation_basis": metadata["interpolation_basis"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
