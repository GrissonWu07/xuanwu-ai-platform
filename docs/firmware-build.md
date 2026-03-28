# esp32鍥轰欢缂栬瘧

## 绗?姝?鍑嗗浣犵殑ota鍦板潃

濡傛灉浣狅紝浣跨敤鐨勬槸鏈」鐩?.3.12鐗堟湰锛屼笉绠℃槸绠€鍗昐erver閮ㄧ讲杩樻槸鍏ㄦā鍧楅儴缃诧紝閮戒細鏈塷ta鍦板潃銆?

鐢变簬绠€鍗昐erver閮ㄧ讲鍜屽叏妯″潡閮ㄧ讲鐨凮TA鍦板潃璁剧疆鏂瑰紡涓嶄竴鏍凤紝璇蜂綘閫夋嫨涓嬮潰鐨勫叿浣撴柟寮忥細

### 濡傛灉浣犵敤鐨勬槸绠€鍗昐erver閮ㄧ讲
姝ゅ埢锛岃浣犵敤娴忚鍣ㄦ墦寮€浣犵殑ota鍦板潃锛屼緥濡傛垜鐨刼ta鍦板潃
```
http://192.168.1.25:8003/xiaozhi/ota/
```
濡傛灉鏄剧ず鈥淥TA鎺ュ彛杩愯姝ｅ父锛屽悜璁惧鍙戦€佺殑websocket鍦板潃鏄細ws://xxx:8000/xiaozhi/v1/

浣犲彲浠ヤ娇鐢ㄩ」鐩嚜甯︾殑`test_page.html`娴嬭瘯涓€涓嬶紝鏄惁鑳借繛涓妎ta椤甸潰杈撳嚭鐨剋ebsocket鍦板潃銆?

濡傛灉璁块棶涓嶅埌锛屼綘闇€瑕佸埌閰嶇疆鏂囦欢`.config.yaml`閲屼慨鏀筦server.websocket`鐨勫湴鍧€锛岄噸鍚悗鍐嶉噸鏂版祴璇曪紝鐩村埌`test_page.html`鑳芥甯歌闂€?

鎴愬姛鍚庯紝璇峰線涓嬭繘琛岀2姝?

### 濡傛灉浣犵敤鐨勬槸鍏ㄦā鍧楅儴缃?
姝ゅ埢锛岃浣犵敤娴忚鍣ㄦ墦寮€浣犵殑ota鍦板潃锛屼緥濡傛垜鐨刼ta鍦板潃
```
http://192.168.1.25:8002/xiaozhi/ota/
```

濡傛灉鏄剧ず鈥淥TA鎺ュ彛杩愯姝ｅ父锛寃ebsocket闆嗙兢鏁伴噺锛歑鈥濄€傞偅灏卞線涓嬭繘琛?姝ャ€?

濡傛灉鏄剧ず鈥淥TA鎺ュ彛杩愯涓嶆甯糕€濓紝澶ф鏄綘杩樻病鍦╜鏅烘帶鍙癭閰嶇疆`Websocket`鍦板潃銆傞偅灏憋細

- 1銆佷娇鐢ㄨ秴绾х鐞嗗憳鐧诲綍鏅烘帶鍙?

- 2銆侀《閮ㄨ彍鍗曠偣鍑籤鍙傛暟绠＄悊`

- 3銆佸湪鍒楄〃涓壘鍒癭server.websocket`椤圭洰锛岃緭鍏ヤ綘鐨刞Websocket`鍦板潃銆備緥濡傛垜鐨勫氨鏄?

```
ws://192.168.1.25:8000/xiaozhi/v1/
```

閰嶇疆瀹屽悗锛屽啀浣跨敤娴忚鍣ㄥ埛鏂颁綘鐨刼ta鎺ュ彛鍦板潃锛岀湅鐪嬫槸涓嶆槸姝ｅ父浜嗐€傚鏋滆繕涓嶆甯稿氨锛屽氨鍐嶆纭涓€涓媁ebsocket鏄惁姝ｅ父鍚姩锛屾槸鍚﹂厤缃簡Websocket鍦板潃銆?

## 绗?姝?閰嶇疆鐜
鍏堟寜鐓ц繖涓暀绋嬮厤缃」鐩幆澧僛銆奧indows鎼缓 ESP IDF 5.3.2寮€鍙戠幆澧冧互鍙婄紪璇戝皬鏅恒€媇(https://icnynnzcwou8.feishu.cn/wiki/JEYDwTTALi5s2zkGlFGcDiRknXf)

## 绗?姝?鎵撳紑閰嶇疆鏂囦欢
閰嶇疆濂界紪璇戠幆澧冨悗锛屼笅杞借櫨鍝aozhi-esp32椤圭洰婧愮爜锛?

浠庤繖閲屼笅杞借櫨鍝xiaozhi-esp32椤圭洰婧愮爜](https://github.com/78/xiaozhi-esp32)銆?

涓嬭浇鍚庯紝鎵撳紑`xiaozhi-esp32/main/Kconfig.projbuild`鏂囦欢銆?

## 绗?姝?淇敼OTA鍦板潃

鎵惧埌`OTA_URL`鐨刞default`鐨勫唴瀹癸紝鎶奰https://api.tenclass.net/xiaozhi/ota/`
   鏀规垚浣犺嚜宸辩殑鍦板潃锛屼緥濡傦紝鎴戠殑鎺ュ彛鍦板潃鏄痐http://192.168.1.25:8002/xiaozhi/ota/`锛屽氨鎶婂唴瀹规敼鎴愯繖涓€?

淇敼鍓嶏細
```
config OTA_URL
    string "Default OTA URL"
    default "https://api.tenclass.net/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```
淇敼鍚庯細
```
config OTA_URL
    string "Default OTA URL"
    default "http://192.168.1.25:8002/xiaozhi/ota/"
    help
        The application will access this URL to check for new firmwares and server address.
```

## 绗?姝?璁剧疆缂栬瘧鍙傛暟

璁剧疆缂栬瘧鍙傛暟

```
# 缁堢鍛戒护琛岃繘鍏iaozhi-esp32鐨勬牴鐩綍
cd xiaozhi-esp32
# 渚嬪鎴戜娇鐢ㄧ殑鏉垮瓙鏄痚sp32s3锛屾墍浠ヨ缃紪璇戠洰鏍囦负esp32s3锛屽鏋滀綘鐨勬澘瀛愭槸鍏朵粬鍨嬪彿锛岃鏇挎崲鎴愬搴旂殑鍨嬪彿
idf.py set-target esp32s3
# 杩涘叆鑿滃崟閰嶇疆
idf.py menuconfig
```

杩涘叆鑿滃崟閰嶇疆鍚庯紝鍐嶈繘鍏Xiaozhi Assistant`锛屽皢`BOARD_TYPE`璁剧疆浣犳澘瀛愮殑鍏蜂綋鍨嬪彿
淇濆瓨閫€鍑猴紝鍥炲埌缁堢鍛戒护琛屻€?

## 绗?姝?缂栬瘧鍥轰欢

```
idf.py build
```

## 绗?姝?鎵撳寘bin鍥轰欢

```
cd scripts
python release.py
```

涓婇潰鐨勬墦鍖呭懡浠ゆ墽琛屽畬鎴愬悗锛屼細鍦ㄩ」鐩牴鐩綍涓嬬殑`build`鐩綍涓嬬敓鎴愬浐浠舵枃浠禶merged-binary.bin`銆?
杩欎釜`merged-binary.bin`灏辨槸瑕佺儳褰曞埌纭欢涓婄殑鍥轰欢鏂囦欢銆?

娉ㄦ剰锛氬鏋滄墽琛屽埌绗簩鍛戒护鍚庯紝鎶ヤ簡鈥渮ip鈥濈浉鍏崇殑閿欒锛岃蹇界暐杩欎釜閿欒锛屽彧瑕乣build`鐩綍涓嬬敓鎴愬浐浠舵枃浠禶merged-binary.bin`
锛屽浣犳病鏈夊お澶у奖鍝嶏紝璇风户缁€?

## 绗?姝?鐑у綍鍥轰欢
   灏唀sp32璁惧杩炴帴鐢佃剳锛屼娇鐢╟hrome娴忚鍣紝鎵撳紑浠ヤ笅缃戝潃

```
https://espressif.github.io/esp-launchpad/
```

鎵撳紑杩欎釜鏁欑▼锛孾Flash宸ュ叿/Web绔儳褰曞浐浠讹紙鏃營DF寮€鍙戠幆澧冿級](https://ccnphfhqs21z.feishu.cn/wiki/Zpz4wXBtdimBrLk25WdcXzxcnNS)銆?
缈诲埌锛歚鏂瑰紡浜岋細ESP-Launchpad 娴忚鍣╓EB绔儳褰昤锛屼粠`3. 鐑у綍鍥轰欢/涓嬭浇鍒板紑鍙戞澘`寮€濮嬶紝鎸夌収鏁欑▼鎿嶄綔銆?

鐑у綍鎴愬姛涓旇仈缃戞垚鍔熷悗锛岄€氳繃鍞ら啋璇嶅敜閱掑皬鏅猴紝鐣欐剰server绔緭鍑虹殑鎺у埗鍙颁俊鎭€?

## 甯歌闂
浠ヤ笅鏄竴浜涘父瑙侀棶棰橈紝渚涘弬鑰冿細

[1銆佷负浠€涔堟垜璇寸殑璇濓紝灏忔櫤璇嗗埆鍑烘潵寰堝闊╂枃銆佹棩鏂囥€佽嫳鏂嘳(./FAQ.md)

[2銆佷负浠€涔堜細鍑虹幇鈥淭TS 浠诲姟鍑洪敊 鏂囦欢涓嶅瓨鍦ㄢ€濓紵](./FAQ.md)

[3銆乀TS 缁忓父澶辫触锛岀粡甯歌秴鏃禲(./FAQ.md)

[4銆佷娇鐢╓ifi鑳借繛鎺ヨ嚜寤烘湇鍔″櫒锛屼絾鏄?G妯″紡鍗存帴涓嶄笂](./FAQ.md)

[5銆佸浣曟彁楂樺皬鏅哄璇濆搷搴旈€熷害锛焆(./FAQ.md)

[6銆佹垜璇磋瘽寰堟參锛屽仠椤挎椂灏忔櫤鑰佹槸鎶㈣瘽](./FAQ.md)

[7銆佹垜鎯抽€氳繃灏忔櫤鎺у埗鐢电伅銆佺┖璋冦€佽繙绋嬪紑鍏虫満绛夋搷浣淽(./FAQ.md)


