#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Koruri のバリアブルフォント版 (Koruri[wght].ttf) を生成するスクリプト
#
# FontForge は可変フォントを出力できないため fontTools で生成する
#   1. Open Sans / M PLUS 1 / Roboto の可変フォントから各ウェイトの静的インスタンスを切り出す
#   2. ウェイトごとに合成してマスターを作る (Open Sans を優先し、Fancy Colon を Roboto から取る)
#   3. マスター群から varLib で可変フォントを組み立てる
#
# 必要なもの: pip install fonttools

import os
import shutil
import tempfile
from copy import deepcopy
from datetime import date

from fontTools.designspaceLib import (
    AxisDescriptor,
    DesignSpaceDocument,
    InstanceDescriptor,
    RuleDescriptor,
    SourceDescriptor,
)
from fontTools.merge import Merger, Options as MergeOptions
from fontTools.merge.cmap import computeMegaGlyphOrder
from fontTools.otlLib.builder import buildStatTable
from fontTools.subset import Options as SubsetOptions, Subsetter
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.scaleUpem import scale_upem
from fontTools.varLib import build as varlib_build
from fontTools.varLib.instancer import instantiateVariableFont

# Open Sans 可変フォントのパス
opensans_vf = "./opensans/OpenSans[wdth,wght].ttf"

# Roboto 可変フォントのパス
roboto_vf = "./roboto/Roboto[wdth,wght].ttf"

# M PLUS 1 可変フォントのパス (M+ 1p の後継)
mplus_vf = "./mplus/MPLUS1[wght].ttf"

# Koruri を生成するディレクトリのパス
koruri_path = "./koruri"

# 出力ファイル名
koruri_vf = "Koruri[wght].ttf"

# EM の大きさ
upm = 2048

# マスターリスト
# Koruri wght, Open Sans wght, Roboto wght, M PLUS 1 wght, スタイル名
# 静的版 koruri.py と同じウェイトの組み合わせにする
master_list = [
    (300, 300, 300, 300, "Light"),
    (400, 400, 400, 400, "Regular"),
    (600, 600, 500, 500, "Semibold"),
    (700, 700, 700, 700, "Bold"),
    (800, 800, 900, 800, "Extrabold"),
]

# 既定のウェイト
default_weight = 400

# Fancy Colon のコードポイント (Roboto の U+EE01 を U+A789 にも割り当てる)
fancy_colon = 0xEE01
modifier_colon = 0xA789

# 縦書きメトリクスの基準にするグリフ
vertical_reference = "uni3042"

def main():
    today = date.today()
    version = "Koruri-{0}".format(today.strftime("%Y%m%d"))

    os.makedirs(koruri_path, exist_ok=True)
    work_dir = tempfile.mkdtemp(dir=koruri_path)
    try:
        opfont = open_unhinted(opensans_vf)
        rbfont = open_unhinted(roboto_vf)
        mpfont = open_unhinted(mplus_vf)

        # M PLUS 1 のウェイト別字形切り替え (rvrn) は、マスターを作る前に取り出しておく
        mp_rules = extract_feature_variations(mpfont)

        masters = []
        for (ko, op, rb, mp, style) in master_list:
            print("Generating master: {0} ({1})".format(style, ko))
            master, mp_names = generate_master(opfont, rbfont, mpfont, op, rb, mp, work_dir)
            set_names(master, style, version)
            master["OS/2"].usWeightClass = ko
            path = os.path.join(work_dir, "Koruri-{0}.ttf".format(style))
            master.save(path)
            masters.append((ko, style, path))

        print("Building variable font")
        rules = build_rules(mp_rules, mp_names)
        vf = build_variable_font(masters, rules, work_dir)
        vf = drop_unused_glyphs(vf)
        finalize(vf)

        out_path = os.path.join(koruri_path, koruri_vf)
        vf.save(out_path)
        print("Saved: {0}".format(out_path))
    finally:
        shutil.rmtree(work_dir)

def open_unhinted(path):
    # 2つのフォントのヒントは合成できないため、ヒントを削除して開く
    font = TTFont(path)
    for tag in ("fpgm", "prep", "cvt ", "cvar", "DSIG"):
        if tag in font:
            del font[tag]
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        glyf[name].removeHinting()
    return font

def instantiate(vf, wght):
    location = {"wght": wght}
    if any(a.axisTag == "wdth" for a in vf["fvar"].axes):
        location["wdth"] = 100
    return instantiateVariableFont(vf, location, inplace=False)

def generate_master(opfont, rbfont, mpfont, op_wght, rb_wght, mp_wght, work_dir):
    # 各フォントの静的インスタンスを切り出す
    op = instantiate(opfont, op_wght)
    rb = instantiate(rbfont, rb_wght)
    mp = instantiate(mpfont, mp_wght)

    # EMの大きさを2048に揃える
    for font in (op, rb, mp):
        if font["head"].unitsPerEm != upm:
            scale_upem(font, upm)

    # Fancy Colon だけを残す
    subset_options = SubsetOptions()
    subset_options.glyph_names = True
    subset_options.notdef_outline = True
    subset_options.layout_features = []
    subsetter = Subsetter(subset_options)
    subsetter.populate(unicodes=[fancy_colon])
    subsetter.subset(rb)

    # Open Sans と Roboto にある文字は M PLUS 1 から外す
    # (重複が残ると fontTools.merge が locl で M PLUS 1 の字形に置き換えてしまう)
    covered = set(op.getBestCmap()) | set(rb.getBestCmap())
    for table in mp["cmap"].tables:
        if table.isUnicode() and table.format != 14:
            for code in covered & set(table.cmap):
                del table.cmap[code]

    # M PLUS 1 に合わせて縦書きメトリクスを付与する
    for font in (op, rb):
        add_vertical_metrics(font, mp)

    # 合成できないテーブルは外しておき、合成後に M PLUS 1 から引き継ぐ
    base = mp["BASE"] if "BASE" in mp else None
    for font in (op, rb, mp):
        for tag in ("gasp", "STAT", "BASE"):
            if tag in font:
                del font[tag]

    # 合成後の M PLUS 1 のグリフ名 (重複した名前は合成時に付け替えられる)
    orders = [list(f.getGlyphOrder()) for f in (op, mp, rb)]
    computeMegaGlyphOrder(Merger(), orders)
    mp_names = dict(zip(mp.getGlyphOrder(), orders[1]))

    paths = []
    for (name, font) in (("op", op), ("mp", mp), ("rb", rb)):
        path = os.path.join(work_dir, "{0}.ttf".format(name))
        font.save(path)
        paths.append(path)

    # Open Sans を優先して合成する (重複するグリフは Open Sans のものが使われる)
    merger = Merger(options=MergeOptions(drop_tables=["DSIG"]))
    master = merger.merge(paths)

    # マスターを保存してもグリフ名が残るようにする
    master["post"].formatType = 2.0
    master["post"].extraNames = []
    master["post"].mapping = {}

    # 行の高さと縦書きのメトリクスは M PLUS 1 に合わせる
    for attr in ("ascent", "descent", "lineGap"):
        setattr(master["hhea"], attr, getattr(mp["hhea"], attr))
    for attr in ("sTypoAscender", "sTypoDescender", "sTypoLineGap"):
        setattr(master["OS/2"], attr, getattr(mp["OS/2"], attr))
    master["vhea"] = deepcopy(mp["vhea"])
    master["vhea"].numberOfVMetrics = len(master["vmtx"].metrics)
    if base is not None:
        master["BASE"] = base

    # Fancy Colon を U+A789 にも割り当てる
    colon = master.getBestCmap().get(fancy_colon)
    if colon is not None:
        for table in master["cmap"].tables:
            if table.isUnicode() and table.format != 14:
                table.cmap[modifier_colon] = colon

    for path in paths:
        os.remove(path)

    return master, mp_names

def extract_feature_variations(vf):
    # GSUB の FeatureVariations を取り外し、
    # [(M PLUS 1 の wght 範囲のリスト, {元グリフ: 置換グリフ}), ...] に変換する
    gsub = vf["GSUB"].table
    fv = getattr(gsub, "FeatureVariations", None)
    if fv is None:
        return []
    gsub.FeatureVariations = None
    gsub.Version = 0x00010000

    axes = [a.axisTag for a in vf["fvar"].axes]
    wght = axes.index("wght")
    records = []
    for record in fv.FeatureVariationRecord:
        ranges = [
            (c.FilterRangeMinValue, c.FilterRangeMaxValue)
            for c in record.ConditionSet.ConditionTable
            if c.AxisIndex == wght
        ]
        lookups = set()
        for sub in record.FeatureTableSubstitution.SubstitutionRecord:
            lookups.update(sub.Feature.LookupListIndex)
        records.append((ranges, lookups))

    # 最初に一致したレコードが使われるので、区間ごとに有効なルックアップを求める
    points = sorted({0.0, 1.0} | {v for (ranges, _) in records for r in ranges for v in r})
    active = {}
    for (lo, hi) in zip(points, points[1:]):
        mid = (lo + hi) / 2
        for (ranges, lookups) in records:
            if all(r[0] <= mid <= r[1] for r in ranges):
                for index in lookups:
                    spans = active.setdefault(index, [])
                    if spans and spans[-1][1] == lo:
                        spans[-1] = (spans[-1][0], hi)
                    else:
                        spans.append((lo, hi))
                break

    fvar = {a.axisTag: a for a in vf["fvar"].axes}["wght"]
    avar = vf["avar"].segments.get("wght") if "avar" in vf else None

    def to_user(value):
        if avar:
            value = piecewise(value, sorted((v, k) for (k, v) in avar.items()))
        if value >= 0:
            return fvar.defaultValue + value * (fvar.maxValue - fvar.defaultValue)
        return fvar.defaultValue + value * (fvar.defaultValue - fvar.minValue)

    rules = []
    for (index, spans) in sorted(active.items()):
        mapping = {}
        for subtable in gsub.LookupList.Lookup[index].SubTable:
            mapping.update(getattr(subtable, "mapping", {}))
        if mapping:
            rules.append(([(to_user(lo), to_user(hi)) for (lo, hi) in spans], mapping))
    return rules

def piecewise(value, points):
    # 折れ線 points 上で value に対応する値を求める
    if value <= points[0][0]:
        return points[0][1]
    for ((x0, y0), (x1, y1)) in zip(points, points[1:]):
        if value <= x1:
            if x1 == x0:
                return y1
            return y0 + (value - x0) * (y1 - y0) / (x1 - x0)
    return points[-1][1]

def build_rules(mp_rules, mp_names):
    # M PLUS 1 の wght を Koruri の wght に読み替えて designspace のルールにする
    to_koruri = sorted((mp, ko) for (ko, _, _, mp, _) in master_list)
    weights = [ko for (ko, _, _, _, _) in master_list]
    rules = []
    for (i, (spans, mapping)) in enumerate(mp_rules):
        rule = RuleDescriptor()
        rule.name = "mplus-{0}".format(i)
        for (lo, hi) in spans:
            lo = max(piecewise(lo, to_koruri), min(weights))
            hi = min(piecewise(hi, to_koruri), max(weights))
            if lo < hi:
                rule.conditionSets.append([{"name": "Weight", "minimum": lo, "maximum": hi}])
        rule.subs = [(mp_names[a], mp_names[b]) for (a, b) in sorted(mapping.items())]
        if rule.conditionSets:
            rules.append(rule)
    return rules

def add_vertical_metrics(font, mp):
    # 縦書きでは全角幅の送りにし、M PLUS 1 と同じ位置に垂直原点を置く
    ref = mp["glyf"][vertical_reference]
    ref.recalcBounds(mp["glyf"])
    advance, ref_tsb = mp["vmtx"][vertical_reference]
    origin = ref.yMax + ref_tsb

    glyf = font["glyf"]
    vmtx = newTable("vmtx")
    vmtx.metrics = {}
    for name in font.getGlyphOrder():
        glyph = glyf[name]
        if glyph.numberOfContours == 0:
            tsb = 0
        else:
            glyph.recalcBounds(glyf)
            tsb = origin - glyph.yMax
        vmtx.metrics[name] = (advance, tsb)
    font["vmtx"] = vmtx
    font["vhea"] = deepcopy(mp["vhea"])
    font["vhea"].numberOfVMetrics = len(vmtx.metrics)

def koruri_names(style, version):
    return (
        (0, """\
Koruri: Copyright (c) 2013- lindwurm.

Open Sans: Copyright 2020 The Open Sans Project Authors.
Roboto: Copyright 2011 The Roboto Project Authors.
M PLUS 1: Copyright 2021 The M+ FONTS Project Authors."""),
        (1, "Koruri {0}".format(style) if style not in ("Regular", "Bold") else "Koruri"),
        (2, style if style in ("Regular", "Bold") else "Regular"),
        (3, "{0};maud;Koruri-{1}".format(version, style)),
        (4, "Koruri {0}".format(style) if style != "Regular" else "Koruri"),
        (5, version),
        (6, "Koruri-{0}".format(style)),
        (11, "https://koruri.github.io"),
        (13, "This Font Software is licensed under the SIL Open Font License, Version 1.1."),
        (14, "https://openfontlicense.org"),
        (16, "Koruri"),
        (17, style),
        (25, "Koruri"),
    )

def set_names(font, style, version):
    name = font["name"]
    name.names = []
    for (name_id, string) in koruri_names(style, version):
        name.setName(string, name_id, 3, 1, 0x409)
        name.setName(string, name_id, 1, 0, 0)
    # 日本語名
    name.setName("Koruri", 16, 3, 1, 0x411)
    name.setName(style, 17, 3, 1, 0x411)

def build_variable_font(masters, rules, work_dir):
    doc = DesignSpaceDocument()

    weights = [ko for (ko, _, _) in masters]
    axis = AxisDescriptor()
    axis.tag = "wght"
    axis.name = "Weight"
    axis.minimum = min(weights)
    axis.default = default_weight
    axis.maximum = max(weights)
    doc.addAxis(axis)

    for (ko, style, path) in masters:
        source = SourceDescriptor()
        source.path = os.path.abspath(path)
        source.styleName = style
        source.familyName = "Koruri"
        source.location = {"Weight": ko}
        doc.addSource(source)

        instance = InstanceDescriptor()
        instance.familyName = "Koruri"
        instance.styleName = style
        instance.postScriptFontName = "Koruri-{0}".format(style)
        instance.location = {"Weight": ko}
        doc.addInstance(instance)

    for rule in rules:
        doc.addRule(rule)

    doc_path = os.path.join(work_dir, "Koruri.designspace")
    doc.write(doc_path)

    vf, _, _ = varlib_build(doc_path)

    # STAT にウェイトごとのスタイル名を登録する
    buildStatTable(vf, [{
        "tag": "wght",
        "name": "Weight",
        "values": [
            {
                "value": ko,
                "name": style,
                "flags": 0x2 if ko == default_weight else 0,
            }
            for (ko, style, _) in masters
        ],
    }], elidedFallbackName=2)
    return vf

def drop_unused_glyphs(font):
    # 合成で使われなくなった M PLUS 1 の重複グリフを取り除く
    # varLib が作る VVAR には VOrgMap が無く、subset が失敗するので補う
    if "VVAR" in font and not hasattr(font["VVAR"].table, "VOrgMap"):
        font["VVAR"].table.VOrgMap = None
    options = SubsetOptions()
    options.glyph_names = True
    options.notdef_outline = True
    options.name_IDs = ["*"]
    options.name_languages = ["*"]
    options.name_legacy = True
    options.layout_features = ["*"]
    options.layout_scripts = ["*"]
    options.legacy_kern = True
    options.drop_tables = [t for t in options.drop_tables if t != "BASE"]
    options.prune_unicode_ranges = False
    options.prune_codepages = False
    subsetter = Subsetter(options)
    subsetter.populate(unicodes=font.getBestCmap().keys())
    subsetter.subset(font)
    return font

def koruri_gasp():
    return {
        8: 0x0002,
        13: 0x000A,
        65535: 0x000A,
    }

def finalize(font):
    font["OS/2"].achVendID = "maud"
    font["OS/2"].usWeightClass = default_weight

    # Grid Fittingの設定
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = koruri_gasp()
    font["gasp"] = gasp

    # 静的版と同じく post テーブルからグリフ名を省く
    font["post"].formatType = 3.0

if __name__ == "__main__":
    main()
