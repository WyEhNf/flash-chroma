"""从已落盘并经看图挑选的照片与创意LUT生成Studio目录，不复制或下载素材。"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# 看过四张100图联系表后人工挑选；标题描述可见内容，不用文件编号推测场景。
PHOTOS = [
    ('div2k-0807', '松林与碧湖', '山水风景', ['湖水', '松林', '蓝绿', '自然光'], '碧绿湖面、松林和木屋同框，适合比较蓝绿色与明暗层次。'),
    ('div2k-0855', '浅蓝帽的人像', '人物肤色', ['人像', '肤色', '针织', '柔光'], '近距离人像与浅蓝帽、灰色针织衣物，观察肤色和柔和中性色。'),
    ('div2k-0846', '仰望城市高楼', '建筑城市', ['建筑', '灰阶', '天空', '线条'], '向上延伸的高楼立面与明亮天空，比较中性色、对比和建筑线条。'),
    ('div2k-0848', '围桌午餐', '缤纷日常', ['餐食', '肤色', '暖色', '俯拍'], '汉堡、薯条和餐具的俯拍场景，同时观察食物暖色与人物手部肤色。'),
    ('div2k-0841', '穹顶下的书廊', '室内暗光', ['室内', '书架', '木纹', '高光'], '深色书架与木地板、明亮穹顶同框，比较暗部细节和高光过渡。'),
    ('div2k-0857', '青蓝叶片特写', '自然纹理', ['多肉', '蓝绿', '柔和渐变', '近景'], '层叠肉质叶片有细微蓝绿差异，适合检查低对比度的颜色渐变。'),
    ('kodak-kodim12', '海边散步', '人物肤色', ['人物', '沙滩', '肤色', '自然光'], '沙滩上的两位人物与浅色海水，比较肤色、红色衣物和自然光。'),
    ('div2k-0808', '静水与白色小舟', '山水风景', ['湖面', '小舟', '山坡', '倒影'], '蓝色水面、岸边木屋与远处山坡，适合比较冷暖和倒影的层次。'),
    ('kodak-kodim08', '彩色木构街屋', '建筑城市', ['街景', '彩色墙面', '木构', '阴影'], '街边彩色木构房屋，兼顾暖色墙面、深色梁柱和街道阴影。'),
    ('div2k-0814', '水岸夜色', '室内暗光', ['夜景', '灯光', '城市', '蓝灰'], '灯光勾勒夜间天际线，蓝灰夜空与水面适合检查暗部层次。'),
    ('div2k-0898', '蓝天下的粉色花枝', '缤纷日常', ['花卉', '粉色', '蓝天', '自然光'], '粉色花枝伸入蓝色天空，比较红蓝分离、浅色花瓣和高饱和色彩。'),
    ('div2k-0872', '核桃与金属夹', '自然纹理', ['核桃', '棕色', '金属', '细节'], '核桃、果仁与金属夹的俯拍细节，比较棕色纹理和明亮高光。'),
    ('div2k-0813', '室内多人肤色', '人物肤色', ['人物', '肤色', '浅色墙面', '红色'], '明亮室内的多人场景，兼看肤色层次、红色衣物与浅色墙面。'),
    ('div2k-0876', '林间步桥', '山水风景', ['树林', '步桥', '绿色', '纵深'], '步桥伸向浓密树林，比较绿色层次、暗部和空间纵深。'),
    ('div2k-0861', '街巷尽头的桥', '建筑城市', ['街道', '砖墙', '桥塔', '冷暖对比'], '砖墙街道框住远处桥塔，观察冷暖对比和街巷暗部细节。'),
    ('div2k-0900', '暖光里的老车', '室内暗光', ['室内', '暖灯', '老车', '阴影'], '老车与陈列架处在暖色灯光下，观察黄色偏色、金属和深色阴影。'),
    ('div2k-0889', '蔬菜摊的绿与红', '缤纷日常', ['蔬菜', '绿色', '红色', '饱和度'], '成筐青椒、红椒与蔬菜，适合比较综合色彩、绿色层次和饱和度。'),
    ('div2k-0899', '逆光下的棕榈叶', '自然纹理', ['叶片', '逆光', '绿色', '细纹'], '阳光穿过绿色叶片，观察绿色明暗层次、叶脉和穿透的高光。'),
    ('kodak-kodim03', '墙上的彩色帽子', '缤纷日常', ['彩色物件', '布料', '高饱和', '阴影'], '黄、橙、绿、粉色帽子沿墙排列，观察高饱和颜色与斜向阴影。'),
    ('div2k-0803', '橙花与绿叶', '缤纷日常', ['花卉', '橙色', '绿叶', '浅景深'], '橙色垂铃状花朵和放射状嫩叶，观察红绿分离及浅景深中的颜色。'),
]

# 仅使用归一化0..1输入域且输出在0..1内的Striped Purple创意CUBE。
# 上游未明确ICC/传递函数，目录不把它们描述为Linear、HDR或色彩空间转换。
LUTS = [
    ('spring-water', 'Spring Water', '清泉', '自然', '保留自然场景的轻盈感，适合从低强度开始。'),
    ('vanilla-bean', 'Vanilla Bean', '香草暖调', '暖调', '抬起暗部并带入轻暖阴影，可少量叠加。'),
    ('horchata', 'Horchata', '米乳柔调', '柔和', '柔化黑位与明亮端，适合人物或日常场景低强度使用。'),
    ('aricha-blend', 'Aricha Blend', '咖啡暖调', '暖调', '暖棕色创意调色，建议轻量使用以保留肤色。'),
    ('amber-haze', 'Amber Haze', '琥珀薄雾', '胶片', '压低明亮端并柔化反差，带来复古雾感。'),
    ('caramel-plum', 'Caramel Plum Cake', '焦糖梅子', '胶片', '抬起暗部的复古配色，适合为餐食或日常照片少量增色。'),
    ('cherry-champagne', 'Cherry Champagne', '樱桃香槟', '柔和', '柔化反差并抬起阴影，少量叠加形成轻淡色调。'),
    ('mint-cream', 'Polaroid Mint Cream', '薄荷奶油', '柔和', '明显抬升黑位、柔化对比的创意配色，宜从低强度试起。'),
    ('grey-matter', 'Grey Matter', '银灰微暖', '低饱和', '显著降低色彩感，保留细微暖色倾向。'),
    ('philly-fog', 'Philly Fog', '城市薄雾', '低饱和', '抬起黑位的雾感调色，适合城市街景的柔和演绎。'),
    ('snowy-blues', 'Snowy Blues', '雪蓝', '冷调', '蓝色倾向的创意调色，用低强度比较建筑、天空和夜景。'),
    ('teal-embers', 'Teal Embers', '青橙余烬', '电影感', '提供青橙方向的创意配色，宜轻度混合。'),
    ('december-greens', 'December Greens', '冬日绿意', '自然', '面向绿植与风景的创意配色，保留调节强度以比较细节。'),
    ('sea-turtle', 'Sea Turtle', '海龟湾', '冷调', '适合在海景与蓝绿场景中低强度尝试的创意配色。'),
    ('seagull-cove', 'Seagull Cove', '海鸥湾', '自然', '为水岸、天空和旅行照片提供另一种柔和配色选择。'),
    ('silent-1920', '1920s', '默片银幕', '黑白', '所有源节点三个输出通道严格相同；满强度时形成黑白影像。'),
    ('classic-1940', '1940s', '经典四十年代', '胶片', '经典年代风格的创意配色，建议轻度使用。'),
    ('film-1970', '1970s', '七十年代暖片', '胶片', '带暖色黑位和柔和明亮端的复古配色。'),
]


def identity():
    return {'lut': 'identity', 'strength': 0.0, 'enabled': False}


def preset(identifier, title, category, description, swatch, selected):
    stages = [{'lut': name, 'strength': strength, 'enabled': True} for name, strength in selected]
    return {'id': identifier, 'title': title, 'category': category, 'description': description,
            'mode': 'creative', 'swatch': swatch, 'stages': stages + [identity() for _ in range(4-len(stages))]}


def presets():
    return [
        preset('natural-clear', '清透自然', '自然', '轻调色，保留原有光线与场景气质。', ['#547e69', '#a3bfc1', '#e3d9c3'], [('spring-water', .18), ('vanilla-bean', .08)]),
        preset('warm-film', '午后暖片', '胶片', '咖啡暖调与轻量年代感，适合日常与旅行。', ['#765341', '#bf9468', '#e9d8b9'], [('aricha-blend', .28), ('film-1970', .18)]),
        preset('cool-city', '冷调城市', '冷调', '以雪蓝和薄雾轻轻调整城市的中性色。', ['#344a5a', '#8298a4', '#d2d8d6'], [('snowy-blues', .25), ('philly-fog', .12)]),
        preset('soft-portrait', '柔光人像', '人像', '柔化反差并保留肤色的细微层次。', ['#c09681', '#dac4b1', '#e5e4dd'], [('horchata', .20), ('vanilla-bean', .10)]),
        preset('mint-afternoon', '奶油午后', '柔和', '浅淡的抬黑与柔和色彩，适合明亮日常。', ['#8aa99c', '#d7d7bd', '#f0e5c9'], [('mint-cream', .24)]),
        preset('amber-dusk', '琥珀暮光', '胶片', '以低强度雾感演绎暖光场景。', ['#6d5c62', '#a88a79', '#d7b68b'], [('amber-haze', .24), ('cherry-champagne', .10)]),
        preset('teal-cinema', '青橙片刻', '电影感', '青橙方向的轻量配色，避免满强度叠加。', ['#376f70', '#a29172', '#d2a67a'], [('teal-embers', .25), ('classic-1940', .12)]),
        preset('quiet-greens', '静谧绿意', '自然', '为绿植加入低饱和的安静层次。', ['#3a5e4b', '#879782', '#c4bba3'], [('december-greens', .20), ('grey-matter', .12)]),
        preset('coast-light', '海岸微光', '自然', '两种低强度水岸配色，比较蓝绿与浅色高光。', ['#3f7e86', '#91bab7', '#dedac4'], [('sea-turtle', .15), ('seagull-cove', .18)]),
        preset('muted-editorial', '低饱和画报', '低饱和', '银灰与薄雾降低色彩感，保留少量原色。', ['#606864', '#99988d', '#d3cbbb'], [('grey-matter', .40), ('philly-fog', .16)]),
        preset('mono-silver', '银幕黑白', '黑白', '单级满强度黑白，其余三级保持恒等。', ['#24272a', '#898b8a', '#e7e5dd'], [('silent-1920', 1.0)]),
        preset('vintage-print', '旧日印相', '胶片', '轻量叠加两种年代风格，保留场景本身的颜色。', ['#695b50', '#a69777', '#d4c7ad'], [('classic-1940', .35), ('film-1970', .12)]),
        preset('caramel-table', '焦糖餐桌', '暖调', '为食物、木纹和日常小物加入轻柔暖意。', ['#7d5541', '#bb8b63', '#e7d5b7'], [('caramel-plum', .24), ('vanilla-bean', .12)]),
        preset('layered-film', '四层轻胶片', '电影感', '四个不同调色级分别低强度工作，可逐级关闭比较。', ['#577a73', '#aea48b', '#cfb495'], [('spring-water', .18), ('vanilla-bean', .14), ('philly-fog', .12), ('film-1970', .16)]),
        preset('clean-base', '原色基线', '自然', '四级均保持恒等，用于与调色结果直接对照。', ['#547b86', '#c0c8ac', '#e2bb8b'], []),
    ]


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def build_catalog(root=ROOT):
    root = Path(root).resolve()
    photo_manifest = read_json(root / 'assets/photos/manifest.json')
    lut_manifest = read_json(root / 'assets/LUT/manifest.json')
    photo_index = {row['id']: row for row in photo_manifest['images']}
    striped = next(row for row in lut_manifest['sources'] if row['id'] == 'stripedpurple')
    lut_index = {Path(row['path']).stem.removeprefix('Striped Purple - '): row
                 for row in lut_manifest['assets'] if row['source_id'] == 'stripedpurple'}
    photo_licenses = {'kodak': 'Kodak来源页声明可不受限制使用；保留摄影者署名',
                      'dped': 'DPED研究数据；保留作者及论文来源，不另行授予许可',
                      'div2k': 'DIV2K仅限学术研究；版权归原权利人'}
    photos = []
    for name, title, category, tags, description in PHOTOS:
        original = photo_index[name]
        image = original['evaluation']
        source = {'dataset': original['dataset'], 'page': original['source_page'], 'url': original['source_url'],
                  'original_sha256': original['original']['sha256'], 'manifest': 'assets/photos/manifest.json'}
        for key in ('archive_member', 'photographer', 'location_as_listed', 'split'):
            if key in original:
                source[key] = original[key]
        photos.append({'id': name, 'path': image['path'], 'title': title, 'category': category, 'tags': tags,
                       'description': description, 'source': source, 'license': photo_licenses[original['dataset']],
                       'license_info': {'statement': photo_manifest['rights'][original['dataset']],
                                        'reference_path': 'assets/photos/README.md', 'source_page': original['source_page']},
                       'sha256': image['sha256'], 'pixel_sha256': image['pixel_sha256'],
                       'width': image['size'][0], 'height': image['size'][1]})
    luts = []
    for identifier, name, title, category, description in LUTS:
        asset = lut_index[name]
        luts.append({'id': identifier, 'path': asset['path'], 'title': title, 'original_title': name,
                     'category': category, 'description': description, 'license': asset['license'],
                     'license_path': striped['license_files'][0]['path'],
                     'license_sha256': striped['license_files'][0]['sha256'],
                     'source': {'provider': 'Striped Purple', 'repo': striped['repo'], 'commit': asset['source_commit'],
                                'url': asset['source_url'], 'source_path': asset['source_path'], 'manifest': 'assets/LUT/manifest.json'},
                     'sha256': asset['sha256'], 'format': asset['format'], 'grid_size': asset['grid_size'],
                     'domain_min': asset['domain_min'], 'domain_max': asset['domain_max'],
                     'output_min': asset['output_min'], 'output_max': asset['output_max'],
                     'embedded_copyright': asset.get('embedded_copyright', []),
                     'input_note': '归一化RGB创意调色；上游未明确ICC或传递函数，不作为Linear或HDR转换。'})
    choices = presets()
    native_manifest = root / 'data/p16-frontier/models/manifest.json'
    native = read_json(native_manifest)
    validation = read_json(root / 'report/data/p16-frontier-header-20261027/results.json')
    for name, title, description, swatch in [
        ('default', 'Cinema · 综合默认', '直接使用已冻结的Cinema四级模型，适合比较既有模型输出。', ['#577979', '#a8a491', '#d2b993']),
        ('max_first', 'Cinema · 均值优先', '直接使用已冻结的Cinema均值优先模型，保留独立验证上下文。', ['#4f6e72', '#a2a58a', '#cfb89b'])]:
        choices.append({'id': 'native-'+name.replace('_', '-'), 'title': title, 'category': '已验模型',
                        'description': description, 'mode': 'native', 'native_profile': name,
                        'native_manifest': 'data/p16-frontier/models/manifest.json',
                        'native_manifest_sha256': digest(native_manifest), 'swatch': swatch,
                        'stages': [identity() for _ in range(4)], 'stages_role': 'native_model_placeholder',
                        'validation_context': {'scope': '固定Cinema四张原始LUT及既有100张1024×768 RGB8照片；不代表任意新LUT。',
                                               'source_luts_sha256': native['profiles'][name]['source_luts_sha256'],
                                               'dataset_pixel_sha256': validation['source_pixels_sha256'],
                                               'image_count': 100, 'evidence': 'report/data/p16-frontier-header-20261027/results.json',
                                               'official_score_available': False}})
    return {'version': 1, 'default_photo': 'div2k-0807', 'default_preset': 'natural-clear',
            'photos': photos, 'luts': luts, 'presets': choices,
            'identity': {'id': 'identity', 'title': '保持原色', 'builtin': True},
            'photo_categories': ['人物肤色', '山水风景', '建筑城市', '室内暗光', '缤纷日常', '自然纹理'],
            'curation': {'contact_sheets_reviewed': ['assets/photos/previews/sheet-01.jpg', 'assets/photos/previews/sheet-02.jpg',
                                                    'assets/photos/previews/sheet-03.jpg', 'assets/photos/previews/sheet-04.jpg'],
                         'expanded_photos_reviewed': ['div2k-0855', 'div2k-0813', 'div2k-0841', 'div2k-0900', 'div2k-0848', 'div2k-0807'],
                         'source_policy': '只引用既有文件，不复制照片，不下载新素材；原许可与作者归属保留。',
                         'presets_scope': '创意预设用于交互观察，不继承Cinema模型精度。stage按顺序混合，关闭级视为identity。',
                         'native_scope': 'native预设的四个identity仅供界面占位，真实处理加载native_profile的四个固定模型。'}}


def validate_catalog(catalog, root=ROOT):
    root = Path(root).resolve()
    if catalog.get('version') != 1 or not 16 <= len(catalog['photos']) <= 20 or not 12 <= len(catalog['luts']) <= 20:
        raise ValueError('Studio目录版本或素材数量不符合约定')
    photo_ids = {row['id'] for row in catalog['photos']}
    lut_ids = {row['id'] for row in catalog['luts']}
    preset_ids = {row['id'] for row in catalog['presets']}
    if len(photo_ids) != len(catalog['photos']) or len(lut_ids) != len(catalog['luts']) or len(preset_ids) != len(catalog['presets']):
        raise ValueError('素材或预设id重复')
    if catalog['default_photo'] not in photo_ids or catalog['default_preset'] not in preset_ids:
        raise ValueError('默认素材或预设不存在')
    photo_manifest = read_json(root / 'assets/photos/manifest.json')
    image_index = {row['id']: row for row in photo_manifest['images']}
    asset_index = {row['path']: row for row in read_json(root / 'assets/LUT/manifest.json')['assets']}
    from PIL import Image
    for row in [*catalog['photos'], *catalog['luts']]:
        path = root / row['path']
        path.resolve().relative_to(root)
        if not path.is_file() or digest(path) != row['sha256']:
            raise ValueError('素材路径或SHA错误：'+row['path'])
        if not row.get('title') or not row.get('license') or not row.get('source'):
            raise ValueError('素材缺少标题、来源或许可')
    for row in catalog['photos']:
        original = image_index[row['id']]['evaluation']
        if original['path'] != row['path'] or original['sha256'] != row['sha256']:
            raise ValueError('照片与原始来源清单不一致')
        with Image.open(root / row['path']) as image:
            image.load()
            if image.mode != 'RGB' or image.size != (1024, 768) or hashlib.sha256(image.tobytes()).hexdigest() != row['pixel_sha256']:
                raise ValueError('照片RGB8尺寸或解码像素SHA不一致')
    grayscale_checked = False
    for row in catalog['luts']:
        asset = asset_index[row['path']]
        if (asset['source_id'] != 'stripedpurple' or row['format'] != 'cube'
                or row['domain_min'] != [0.0]*3 or row['domain_max'] != [1.0]*3
                or min(row['output_min']) < 0 or max(row['output_max']) > 1):
            raise ValueError('LUT不属于选定的归一化创意RGB集合')
        if digest(root / row['license_path']) != row['license_sha256']:
            raise ValueError('LUT许可文件摘要不同')
        if row['id'] == 'silent-1920':
            nodes = 0
            for line in (root / row['path']).read_text(encoding='utf-8-sig').splitlines():
                fields = line.strip().split()
                if len(fields) != 3:
                    continue
                try:
                    channels = [float(value) for value in fields]
                except ValueError:
                    continue
                if channels[0] != channels[1] or channels[0] != channels[2]:
                    raise ValueError('黑白LUT含不同的RGB输出通道')
                nodes += 1
            if nodes != row['grid_size']**3:
                raise ValueError('黑白LUT节点数不符')
            grayscale_checked = True
    for choice in catalog['presets']:
        if len(choice['stages']) != 4 or len(choice['swatch']) != 3 or any(not re.fullmatch('#[0-9a-fA-F]{6}', colour) for colour in choice['swatch']):
            raise ValueError('预设需要固定四级和三个色签')
        for stage in choice['stages']:
            if stage['lut'] not in lut_ids | {'identity'} or type(stage['enabled']) is not bool or not 0 <= stage['strength'] <= 1:
                raise ValueError('预设引用或强度非法')
        if choice['mode'] == 'native':
            if choice['native_profile'] not in ('default', 'max_first') or choice['stages'] != [identity() for _ in range(4)]:
                raise ValueError('native预设不得把占位级误当真实模型')
            if digest(root / choice['native_manifest']) != choice['native_manifest_sha256']:
                raise ValueError('native模型清单SHA改变')
    if not grayscale_checked:
        raise ValueError('未验证黑白素材')
    return {'photos': len(photo_ids), 'luts': len(lut_ids), 'presets': len(preset_ids),
            'categories': sorted({row['category'] for row in catalog['photos']}),
            'paths_and_file_sha256': '通过', 'photo_pixel_sha256': '通过', 'strict_grayscale_nodes': '通过',
            'scope': '素材身份、RGB8尺寸、目录引用及许可检查；未运行性能测试或宣称创意预设精度。'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'gui/studio_catalog.json')
    parser.add_argument('--check', action='store_true', help='只核对现有目录与维护来源，不写文件')
    args = parser.parse_args()
    value = build_catalog()
    summary = validate_catalog(value)
    if args.check:
        if read_json(args.output) != value:
            raise ValueError('目录与生成来源不同，请重新生成')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
