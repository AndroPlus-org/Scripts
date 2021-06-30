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

### 手動

* [ここ](https://github.com/coz-m/MPLUS_FONTS) から最新の Mplus 1 をダウンロード
* Mplus 1 を `mplus` に展開

### FontForge interactive console

```
fontforge -lang=py -script mejiro.py
```
