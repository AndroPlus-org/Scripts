#!/bin/bash

bldblu=${txtbld}$(tput setaf 4)

# スクリプトのあるディレクトリで実行する
cd "$(dirname "$0")" || exit 1

# ダウンロード先のフォルダに前回の中身が残っていれば削除する (.gitkeep は残す)
for dir in opensans roboto mplus; do
	mkdir -p "$dir"
	find "$dir" -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
done

# Open Sans と Roboto は Google Fonts の可変フォントを取得し、
# koruri.py (font_list) で使うウェイトの静的フォントを fontTools で切り出す
# (fonts.google.com/download は wget で zip を取得できないため)
gf=https://raw.githubusercontent.com/google/fonts/main/ofl
wget "$gf/opensans/OpenSans%5Bwdth,wght%5D.ttf" -O "opensans/OpenSans[wdth,wght].ttf"
wget "$gf/roboto/Roboto%5Bwdth,wght%5D.ttf" -O "roboto/Roboto[wdth,wght].ttf"

# ファイル名:wght
opensans_list="Light:300 Regular:400 SemiBold:600 Bold:700 ExtraBold:800"
roboto_list="Light:300 Regular:400 Medium:500 Bold:700 Black:900"

for item in $opensans_list; do
	python3 -m fontTools.varLib.instancer "opensans/OpenSans[wdth,wght].ttf" \
		wght=${item#*:} wdth=100 --update-name-table -q -o "opensans/OpenSans-${item%:*}.ttf" || exit 1
done
for item in $roboto_list; do
	python3 -m fontTools.varLib.instancer "roboto/Roboto[wdth,wght].ttf" \
		wght=${item#*:} wdth=100 --update-name-table -q -o "roboto/Roboto-${item%:*}.ttf" || exit 1
done

# M+ 1p (M+ OUTLINE FONTS TESTFLIGHT 063)
# 配布元の OSDN は終了したため、Ubuntu のアーカイブにある元の tarball から取得する
wget https://archive.ubuntu.com/ubuntu/pool/universe/f/fonts-mplus/fonts-mplus_063.orig.tar.xz -O mplus/mplus.tar.xz
tar xJf mplus/mplus.tar.xz -C mplus --strip-components=1 --wildcards '*/mplus-1p-*.ttf'
rm mplus/mplus.tar.xz

# バリアブルフォント版 (koruri_vf.py) 用
wget "$gf/mplus1/MPLUS1%5Bwght%5D.ttf" -O "mplus/MPLUS1[wght].ttf"

echo "${bldblu}                        **                        "
echo "${bldblu}                      **# **                      "
echo "${bldblu}                    **##### **                    "
echo "${bldblu}                  **######### **                  "
echo "${bldblu}                **############# **                "
echo "${bldblu}              **################# **              "
echo "${bldblu}            **##################### **            "
echo "${bldblu}          **###***      *****######## **          "
echo "${bldblu}        **##**        ***    ***####### **        "
echo "${bldblu}      **##**         *###*      ***###### **      "
echo "${bldblu}    **###*            ****         *****### **    "
echo "${bldblu}  **####*                     ***############ **  "
echo "${bldblu} **###**                    **#################** "
echo "${bldblu}  ****                     *##################**  "
echo "${bldblu}                          *#################**    "
echo "${bldblu}                         *|###############**      "
echo "${bldblu}                         *##############**        "
echo "${bldblu}                         *############**          "
echo "${bldblu}                         *##########**            "
echo "${bldblu}                         |########**              "
echo "${bldblu}                        *#######**                "
echo "${bldblu}                       * #####**                  "
echo "${bldblu}                      *#####**                    "
echo "${bldblu}                      ** #**                      "
echo "${bldblu}                        **                        "

echo "Koruri を生成するには FontForge をインストールし、"
echo "以下を実行してください"
echo "fontforge -lang=py -script koruri.py"
echo ""
echo "バリアブルフォント版は fonttools をインストールした後、以下を実行してください"
echo "python3 koruri_vf.py"
tput sgr0
