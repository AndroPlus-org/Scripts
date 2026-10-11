#!/bin/bash

bldblu=${txtbld}$(tput setaf 4)

# スクリプトのあるディレクトリで実行する
cd "$(dirname "$0")" || exit 1

# ダウンロード先のフォルダに前回の中身が残っていれば削除する (.gitkeep は残す)
for dir in opensans roboto mplus; do
	mkdir -p "$dir"
	find "$dir" -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
done

# fonts.google.com/download は JavaScript でダウンロードする HTML を返すようになり、
# wget では zip を取得できないため、配布元のリポジトリから直接取得する

# Open Sans (Google Fonts と同じ v3 の静的フォント)
for weight in Light Regular SemiBold Bold ExtraBold; do
	wget "https://raw.githubusercontent.com/googlefonts/opensans/main/fonts/ttf/OpenSans-$weight.ttf" -O "opensans/OpenSans-$weight.ttf"
done

# Roboto (Fancy Colon のみ使用)
for weight in Light Regular Medium Bold Black; do
	wget "https://raw.githubusercontent.com/googlefonts/roboto/main/src/hinted/Roboto-$weight.ttf" -O "roboto/Roboto-$weight.ttf"
done

# M+ 1p (M+ OUTLINE FONTS TESTFLIGHT 063)
# 配布元の OSDN は終了したため、Ubuntu のアーカイブにある元の tarball から取得する
wget https://archive.ubuntu.com/ubuntu/pool/universe/f/fonts-mplus/fonts-mplus_063.orig.tar.xz -O mplus/mplus.tar.xz
tar xJf mplus/mplus.tar.xz -C mplus --strip-components=1 --wildcards '*/mplus-1p-*.ttf'
rm mplus/mplus.tar.xz

# バリアブルフォント版 (koruri_vf.py) 用
gf=https://raw.githubusercontent.com/google/fonts/main/ofl
wget "$gf/opensans/OpenSans%5Bwdth,wght%5D.ttf" -O "opensans/OpenSans[wdth,wght].ttf"
wget "$gf/roboto/Roboto%5Bwdth,wght%5D.ttf" -O "roboto/Roboto[wdth,wght].ttf"
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
