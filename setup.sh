#!/bin/bash

bldblu=${txtbld}$(tput setaf 4)

mkdir -p mejiro mplus roboto
cd roboto
wget https://fonts.google.com/download?family=Roboto -O roboto.zip
unzip roboto.zip
cd ../

# バリアブルフォント版 (mejiro_vf.py) 用
gf=https://raw.githubusercontent.com/google/fonts/main/ofl
wget "$gf/roboto/Roboto%5Bwdth,wght%5D.ttf" -O "roboto/Roboto[wdth,wght].ttf"
wget "$gf/mplus1/MPLUS1%5Bwght%5D.ttf" -O "mplus/MPLUS1[wght].ttf"

echo "Mejiro を生成するには FontForge をインストールし、"
echo "最新の mplus-TESTFLIGHT-*.tar.xz を"
echo "https://ja.osdn.net/projects/mplus-fonts/releases/62344"
echo "からダウンロードして mplus/ に展開した後、以下を実行してください"
echo "fontforge -lang=py -script mejiro.py"
echo ""
echo "バリアブルフォント版は fonttools をインストールした後、以下を実行してください"
echo "python3 mejiro_vf.py"
tput sgr0
