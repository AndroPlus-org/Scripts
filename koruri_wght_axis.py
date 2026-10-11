#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# 生成済みの Koruri (静的フォント) に fvar / gvar / STAT を追加し、
# 見た目を一切変えずに「バリアブルフォントとして扱える」フォントにする。
#
# M+ 1p はウェイト間でアウトラインの点構造が一致しないため、
# 補間可能な本物のバリアブルフォントは作れない。
# そこで各ウェイトのファイルに wght 軸だけを持たせ、変化量 (delta) は 0 にする。
# wght を指定されてもアウトラインは変わらず、そのファイルのウェイトで描画される。
#
# Android 16 以降でアプリがフォントにバリエーション (wght など) を要求した際、
# 静的フォントが可変フォントとして扱われてクラッシュする問題の回避を目的とする。
#
# 使い方:
#   pip install fonttools
#   python3 koruri_wght_axis.py                       # ./koruri -> ./koruri-wght
#   python3 koruri_wght_axis.py ./ohruri ./ohruri-wght  # Ohruri の場合

import glob
import os
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables._f_v_a_r import Axis, NamedInstance

# wght 軸の範囲
# 範囲外の値は丸められるが、要求され得る値をすべて含めておく
WGHT_MIN = 100
WGHT_MAX = 900

# ファイル名のウェイト -> wght 軸のデフォルト値
# Magisk モジュールの fonts.xml で指定している weight に合わせる
WEIGHT_MAP = {
    "Thin": 100,
    "Light": 300,
    "Regular": 400,
    "Medium": 500,
    "Semibold": 600,
    "Bold": 700,
    "Extrabold": 800,
    "Black": 900,
}


def weight_value(font, path):
    name = os.path.splitext(os.path.basename(path))[0].split("-")[-1]
    if name in WEIGHT_MAP:
        return name, WEIGHT_MAP[name]
    return name, font["OS/2"].usWeightClass


def make_vf(src, dst):
    font = TTFont(src)
    if "fvar" in font:
        print("skip (already variable): {0}".format(src))
        return

    style, default = weight_value(font, src)
    name = font["name"]

    # fvar: wght 軸と、このファイル自身の名前付きインスタンス 1 つ
    axis = Axis()
    axis.axisTag = "wght"
    axis.minValue = WGHT_MIN
    axis.defaultValue = default
    axis.maxValue = WGHT_MAX
    axis.axisNameID = name.addMultilingualName({"en": "Weight"}, minNameID=256)

    instance = NamedInstance()
    instance.subfamilyNameID = name.addMultilingualName({"en": style}, minNameID=256)
    instance.postscriptNameID = 6
    instance.coordinates = {"wght": default}

    fvar = newTable("fvar")
    fvar.axes = [axis]
    fvar.instances = [instance]
    font["fvar"] = fvar

    # gvar: 全グリフ変化なし
    gvar = newTable("gvar")
    gvar.version = 1
    gvar.reserved = 0
    gvar.variations = {glyph: [] for glyph in font.getGlyphOrder()}
    font["gvar"] = gvar

    # STAT
    buildStatTable(
        font,
        [{"tag": "wght", "name": "Weight",
          "values": [{"value": default, "name": style,
                      "flags": 0x2 if default == 400 else 0}]}],
        elidedFallbackName=2,
    )

    font.save(dst)
    print("{0} -> {1} (wght {2}..{3}, default {4})".format(
        src, dst, WGHT_MIN, WGHT_MAX, default))


def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else "./koruri"
    dst_dir = sys.argv[2] if len(sys.argv) > 2 else src_dir.rstrip("/") + "-wght"
    os.makedirs(dst_dir, exist_ok=True)

    paths = sorted(glob.glob(os.path.join(src_dir, "*.ttf")))
    if not paths:
        sys.exit("No TTF found in {0}".format(src_dir))
    for path in paths:
        make_vf(path, os.path.join(dst_dir, os.path.basename(path)))


if __name__ == "__main__":
    main()
