#!/bin/bash

bldblu=${txtbld}$(tput setaf 4)

mkdir -p mejiro mplus roboto
cd roboto
wget https://fonts.google.com/download?family=Roboto -O roboto.zip
unzip roboto.zip
cd ../

echo "Mejiro を生成するには FontForge をインストールし、"
echo "最新の mplus-TESTFLIGHT-*.tar.xz を"
echo "https://ja.osdn.net/projects/mplus-fonts/releases/62344"
echo "からダウンロードして mplus/ に展開した後、以下を実行してください"
echo "fontforge -lang=py -script mejiro.py"
tput sgr0
