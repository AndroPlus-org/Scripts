# Scripts

[Koruri](https://koruri.github.io/) をビルドするためのスクリプトです。

## 使い方

```
git clone https://github.com/Koruri/Scripts.git make_koruri
```

```
cd make_koruri
```

Open Sans と Roboto は `setup.sh` の中でダウンロード、展開されます。

```
./setup.sh
```

あとは

* [ここ](https://osdn.jp/projects/mplus-fonts/releases/62344) から最新の `M+ OUTLINE FONTS TESTFLIGHT` をダウンロード
* M+ 1p を `mplus` に展開
* [FontForge](https://fontforge.org/) をインストールしておく

```
fontforge -lang=py -script koruri.py
```

## バリアブルフォント版

Open Sans・Roboto・M PLUS 1（M+ 1p の後継）の可変フォントを合成し、ウェイト軸（300〜800）を持つ `koruri/Koruri[wght].ttf` を生成します。

* 素材の可変フォントは `setup.sh` の中で Google Fonts のリポジトリからダウンロードされます
* [fontTools](https://github.com/fonttools/fonttools) をインストールしておく（FontForge は不要）

```
pip install fonttools
```

```
python3 koruri_vf.py
```

静的版との違い

* 和文は M+ 1p ではなく M PLUS 1 を使うため、和文の字形が少し異なります
* 名前付きインスタンスは Light / Regular / Semibold / Bold / Extrabold で、静的版と同じウェイトの組み合わせを使います
* M PLUS 1 のウェイトによる字形の切り替え（rvrn）は引き継いでいます
* 素材のライセンスに合わせ、SIL Open Font License 1.1 として名前テーブルに記載しています
* ヒントは含みません

