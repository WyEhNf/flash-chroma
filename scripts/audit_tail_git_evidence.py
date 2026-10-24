"""逐Git blob核对本轮证据manifest，并独立核对源码ZIP的测量字节。"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile
ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-ref', default='HEAD')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    folders = ['channel-tail-nodes-20261023', 'channel-tail-extensions-20261024', 'cinema-last-stage-20261024',
               'protected-tail-cases-20261024', 'velvia-body-diagonals-20261024', 'velvia-cell-diagonals-20261024',
               'velvia-stripe-diagonals-20261024', 'velvia-stripe-nodes-20261024', 'velvia-mean-first-20261024',
               'velvia-bubble-probe-20261024', 'velvia-bubble-slope-20261024', 'velvia-bubble-accept-20261024',
               'velvia-bubble-native-20261024', 'velvia-bubble-perf-20261024', 'p16-direct-u16-native-20261024-v2',
               'p16-direct-u16-perf-20261024', 'p16-direct-u16-ilp-native-20261024', 'p16-direct-u16-ilp-perf-20261024',
               'p16-cinema-first-hotspot-20261024', 'p16-cinema-first-joint-20261024', 'p16-cinema-first-box-20261024',
               'p16-cinema-first-group-20261024', 'p16-cinema-first-cpsat-20261024',
               'p16-cinema-first-risk-20261024', 'p16-cinema-first-safe-cpsat-20261024',
               'p16-cinema-first-error-cost-census-20261024', 'p16-cinema-max48-pareto-quality-20261024',
               'p16-cinema-first-narrow-cost-census-20261024', 'p16-cinema-first-direct-budget-20261024',
               'p16-cinema-max48-first-box-20261024', 'p16-cinema-max48-risk-upper-20261024',
               'p16-cinema-max48-training-bridge-20261024',
               'p16-cinema-current-safe-cpsat-20261024', 'p16-cinema-current-feasible-cpsat-20261024',
               'p16-cinema-current-full-quality-20261024']
    checks, failures = [], []
    for folder in folders:
        relative = 'report/data/'+folder
        manifest = json.loads(subprocess.check_output(['git', 'show', args.git_ref+':'+relative+'/manifest.json'], cwd=ROOT))
        for name, expected in manifest['files'].items():
            path = relative+'/'+name
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+path], cwd=ROOT)
            result = {'kind': 'git_blob', 'path': path, 'expected_sha256': expected, 'actual_sha256': digest(blob)}
            result['pass'] = result['expected_sha256'] == result['actual_sha256']
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        reused = manifest.get('reused_cell_statistics')
        if reused:
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+reused['path']], cwd=ROOT)
            result = {'kind': 'reused_git_blob', 'path': reused['path'], 'expected_sha256': reused['sha256'],
                      'actual_sha256': digest(blob), 'pass': digest(blob) == reused['sha256']}
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        reused = manifest.get('reused_full_support_manifest')
        if reused:
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+reused['path']], cwd=ROOT)
            result = {'kind': 'reused_full_support_manifest', 'path': reused['path'], 'expected_sha256': reused['sha256'],
                      'actual_sha256': digest(blob), 'pass': digest(blob) == reused['sha256']}
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        reused = manifest.get('reused_risk_manifest')
        if reused:
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+reused['path']], cwd=ROOT)
            result = {'kind': 'reused_risk_manifest', 'path': reused['path'], 'expected_sha256': reused['sha256'],
                      'actual_sha256': digest(blob), 'pass': digest(blob) == reused['sha256']}
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        reused = manifest.get('reused_witness_manifest')
        if reused:
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+reused['path']], cwd=ROOT)
            result = {'kind': 'reused_witness_manifest', 'path': reused['path'], 'expected_sha256': reused['sha256'],
                      'actual_sha256': digest(blob), 'pass': digest(blob) == reused['sha256']}
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        reused = manifest.get('reused_error_cost_manifest')
        if reused:
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+reused['path']], cwd=ROOT)
            result = {'kind': 'reused_error_cost_manifest', 'path': reused['path'], 'expected_sha256': reused['sha256'],
                      'actual_sha256': digest(blob), 'pass': digest(blob) == reused['sha256']}
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        for field in ('reused_environment_manifest', 'reused_narrow_census_manifest',
                      'reused_box_contract_manifest', 'reused_quality_manifest', 'reused_max48_box_manifest',
                      'reused_max48_risk_manifest', 'reused_current_minl1_manifest', 'reused_current_feasible_manifest'):
            reused = manifest.get(field)
            if not reused:
                continue
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+reused['path']], cwd=ROOT)
            result = {'kind': field, 'path': reused['path'], 'expected_sha256': reused['sha256'],
                      'actual_sha256': digest(blob), 'pass': digest(blob) == reused['sha256']}
            checks.append(result)
            if not result['pass']:
                failures.append(result)
        source = subprocess.check_output(['git', 'show', args.git_ref+':'+relative+'/source.zip'], cwd=ROOT)
        with zipfile.ZipFile(io.BytesIO(source)) as archive:
            for name, expected in manifest['source_sha256'].items():
                actual = digest(archive.read(name))
                result = {'kind': 'measured_source_zip', 'path': relative+'/source.zip!/'+name,
                          'expected_sha256': expected, 'actual_sha256': actual, 'pass': actual == expected}
                checks.append(result)
                if not result['pass']:
                    failures.append(result)
        for zip_name, field in (('support-evidence.zip', 'support_member_sha256'), ('models.zip', 'model_member_sha256')):
            if field not in manifest:
                continue
            blob = subprocess.check_output(['git', 'show', args.git_ref+':'+relative+'/'+zip_name], cwd=ROOT)
            with zipfile.ZipFile(io.BytesIO(blob)) as archive:
                for name, expected in manifest[field].items():
                    actual = digest(archive.read(name))
                    result = {'kind': field, 'path': relative+'/'+zip_name+'!/'+name,
                              'expected_sha256': expected, 'actual_sha256': actual, 'pass': actual == expected}
                    checks.append(result)
                    if not result['pass']:
                        failures.append(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    record = {'pass': not failures, 'git_ref': args.git_ref, 'checked_commit': subprocess.check_output(
        ['git', 'rev-parse', args.git_ref], cwd=ROOT, text=True).strip(), 'checks': checks, 'failures': failures,
        'scope': 'raw证据按实际Git blob字节验SHA；源码SHA按该阶段冻结source.zip字节核，不要求后续修改过的HEAD源码等于历史快照。没有重新运行数值或计时。'}
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'pass': record['pass'], 'checks': len(checks), 'failures': failures}, ensure_ascii=False), flush=True)
    if failures:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
