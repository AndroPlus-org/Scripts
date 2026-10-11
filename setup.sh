#!/bin/bash

bldblu=${txtbld}$(tput setaf 4)

cd opensans
wget https://fonts.google.com/download?family=Open+Sans -O opensans.zip
unzip opensans.zip
cd ../

cd roboto
wget https://fonts.google.com/download?family=Roboto -O roboto.zip
unzip roboto.zip
cd ../

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
echo "最新の M+ 1p を mplus/ に展開した後、以下を実行してください"
echo "fontforge -lang=py -script koruri.py"
echo ""
echo "バリアブルフォント版は fonttools をインストールした後、以下を実行してください"
echo "python3 koruri_vf.py"
tput sgr0
