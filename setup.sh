#!/bin/bash

bldblu=${txtbld}$(tput setaf 4)

# スクリプトのあるディレクトリで実行する
cd "$(dirname "$0")" || exit 1

# ダウンロード先のフォルダに前回の中身が残っていれば削除する (.gitkeep は残す)
for dir in opensans roboto mplus; do
	mkdir -p "$dir"
	find "$dir" -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
done

# Google Fonts の zip は可変フォントと static/ フォルダに分かれているため、
# static/ の静的フォントを各ディレクトリの直下に置く
cd opensans
wget https://fonts.google.com/download?family=Open+Sans -O opensans.zip
unzip -o opensans.zip
if [ -d static ]; then cp static/*.ttf ./; fi
cd ../

cd roboto
wget https://fonts.google.com/download?family=Roboto -O roboto.zip
unzip -o roboto.zip
if [ -d static ]; then cp static/*.ttf ./; fi
cd ../

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
