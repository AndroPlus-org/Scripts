# Scripts

Mejiro をビルドするためのスクリプトです。

## 使い方

```
git clone https://github.com/AndroPlus-org/Scripts make_mejiro
```

```
cd make_mejiro
```

```
bash setup.sh
```

```
fontforge -lang=py -script mejiro.py
```

## バリアブルフォント版

Roboto と M PLUS 1（M+ 1p の後継）の可変フォントを合成し、ウェイト軸（100〜800）を持つ `mejiro/Mejiro[wght].ttf` を生成します。

* 素材の可変フォントは `setup.sh` の中で Google Fonts のリポジトリからダウンロードされます
* [fontTools](https://github.com/fonttools/fonttools) をインストールしておく（FontForge は不要）

```
pip install fonttools
```

```
python3 mejiro_vf.py
```

静的版との違い

* 和文は M+ 1p ではなく M PLUS 1 を使うため、和文の字形が少し異なります
* 名前付きインスタンスは Thin / Light / Regular / Semibold / Bold / Extrabold で、静的版と同じウェイトの組み合わせを使います
* M PLUS 1 のウェイトによる字形の切り替え（rvrn）は引き継いでいます
* 静的版と同じく kern は削除し、ヒントは Roboto のものを使います
* 素材のライセンスに合わせ、SIL Open Font License 1.1 として名前テーブルに記載しています

