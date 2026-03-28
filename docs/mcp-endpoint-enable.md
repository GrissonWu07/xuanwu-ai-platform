# MCP 鎺ュ叆鐐归儴缃蹭娇鐢ㄦ寚鍗?

鏈暀绋嬪寘鍚?涓儴鍒?
- 1銆佸浣曢儴缃睲CP鎺ュ叆鐐硅繖涓湇鍔?
- 2銆佸叏妯″潡閮ㄧ讲鏃讹紝鎬庝箞閰嶇疆MCP鎺ュ叆鐐?
- 3銆佸崟妯″潡閮ㄧ讲鏃讹紝鎬庝箞閰嶇疆MCP鎺ュ叆鐐?

# 1銆佸浣曢儴缃睲CP鎺ュ叆鐐硅繖涓湇鍔?

## 绗竴姝ワ紝涓嬭浇mcp鎺ュ叆鐐归」鐩簮鐮?

娴忚鍣ㄦ墦寮€[mcp鎺ュ叆鐐归」鐩湴鍧€](https://github.com/xinnan-tech/mcp-endpoint-server)

鎵撳紑瀹岋紝鎵惧埌椤甸潰涓竴涓豢鑹茬殑鎸夐挳锛屽啓鐫€`Code`鐨勬寜閽紝鐐瑰紑瀹冿紝鐒跺悗浣犲氨鐪嬪埌`Download ZIP`鐨勬寜閽€?

鐐瑰嚮瀹冿紝涓嬭浇鏈」鐩簮鐮佸帇缂╁寘銆備笅杞藉埌浣犵數鑴戝悗锛岃В鍘嬪畠锛屾鏃跺畠鐨勫悕瀛楀彲鑳藉彨`mcp-endpoint-server-main`
浣犻渶瑕佹妸瀹冮噸鍛藉悕鎴恅mcp-endpoint-server`銆?

## 绗簩姝ワ紝鍚姩绋嬪簭
杩欎釜椤圭洰鏄竴涓緢绠€鍗曠殑椤圭洰锛屽缓璁娇鐢╠ocker杩愯銆備笉杩囧鏋滀綘涓嶆兂浣跨敤docker杩愯锛屼綘鍙互鍙傝€僛杩欎釜椤甸潰](https://github.com/xinnan-tech/mcp-endpoint-server/blob/main/README_dev.md)浣跨敤婧愮爜杩愯銆備互涓嬫槸docker杩愯鐨勬柟娉?

```
# 杩涘叆鏈」鐩簮鐮佹牴鐩綍
cd mcp-endpoint-server

# 娓呴櫎缂撳瓨
docker compose -f docker-compose.yml down
docker stop mcp-endpoint-server
docker rm mcp-endpoint-server
docker rmi ghcr.nju.edu.cn/xinnan-tech/mcp-endpoint-server:latest

# 鍚姩docker瀹瑰櫒
docker compose -f docker-compose.yml up -d
# 鏌ョ湅鏃ュ織
docker logs -f mcp-endpoint-server
```

姝ゆ椂锛屾棩蹇楅噷浼氳緭鍑虹被浼间互涓嬬殑鏃ュ織
```
250705 INFO-=====涓嬮潰鐨勫湴鍧€鍒嗗埆鏄櫤鎺у彴/鍗曟ā鍧桵CP鎺ュ叆鐐瑰湴鍧€====
250705 INFO-鏅烘帶鍙癕CP鍙傛暟閰嶇疆: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
250705 INFO-鍗曟ā鍧楅儴缃睲CP鎺ュ叆鐐? ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
250705 INFO-=====璇锋牴鎹叿浣撻儴缃查€夋嫨浣跨敤锛岃鍕挎硠闇茬粰浠讳綍浜?=====
```

璇蜂綘鎶婁袱涓帴鍙ｅ湴鍧€澶嶅埗鍑烘潵锛?

鐢变簬浣犳槸docker閮ㄧ讲锛屽垏涓嶅彲鐩存帴浣跨敤涓婇潰鐨勫湴鍧€锛?

鐢变簬浣犳槸docker閮ㄧ讲锛屽垏涓嶅彲鐩存帴浣跨敤涓婇潰鐨勫湴鍧€锛?

鐢变簬浣犳槸docker閮ㄧ讲锛屽垏涓嶅彲鐩存帴浣跨敤涓婇潰鐨勫湴鍧€锛?

浣犲厛鎶婂湴鍧€澶嶅埗鍑烘潵锛屾斁鍦ㄤ竴涓崏绋块噷锛屼綘瑕佺煡閬撲綘鐨勭數鑴戠殑灞€鍩熺綉ip鏄粈涔堬紝渚嬪鎴戠殑鐢佃剳灞€鍩熺綉ip鏄痐192.168.1.25`锛岄偅涔?
鍘熸潵鎴戠殑鎺ュ彛鍦板潃
```
鏅烘帶鍙癕CP鍙傛暟閰嶇疆: http://172.22.0.2:8004/mcp_endpoint/health?key=abc
鍗曟ā鍧楅儴缃睲CP鎺ュ叆鐐? ws://172.22.0.2:8004/mcp_endpoint/mcp/?token=def
```
灏辫鏀规垚
```
鏅烘帶鍙癕CP鍙傛暟閰嶇疆: http://192.168.1.25:8004/mcp_endpoint/health?key=abc
鍗曟ā鍧楅儴缃睲CP鎺ュ叆鐐? ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

鏀瑰ソ鍚庯紝璇蜂娇鐢ㄦ祻瑙堝櫒鐩存帴璁块棶`鏅烘帶鍙癕CP鍙傛暟閰嶇疆`銆傚綋娴忚鍣ㄥ嚭鐜扮被浼艰繖鏍风殑浠ｇ爜锛岃鏄庢槸鎴愬姛浜嗐€?
```
{"result":{"status":"success","connections":{"tool_connections":0,"robot_connections":0,"total_connections":0}},"error":null,"id":null,"jsonrpc":"2.0"}
```

璇蜂綘淇濈暀濂戒笂闈袱涓猔鎺ュ彛鍦板潃`锛屼笅涓€姝ヨ鐢ㄥ埌銆?

# 2銆佸叏妯″潡閮ㄧ讲鏃讹紝鎬庝箞閰嶇疆MCP鎺ュ叆鐐?
棣栧厛锛屼綘瑕佸紑鍚疢CP鎺ュ叆鐐瑰姛鑳姐€傚湪鏅烘帶鍙帮紝鐐瑰嚮椤堕儴`鍙傛暟瀛楀吀`锛屽湪涓嬫媺鑿滃崟涓紝鐐瑰嚮`绯荤粺鍔熻兘閰嶇疆`椤甸潰銆傚湪椤甸潰涓婂嬀閫塦MCP鎺ュ叆鐐筦锛岀偣鍑籤淇濆瓨閰嶇疆`銆傚湪`瑙掕壊閰嶇疆`椤甸潰锛岀偣鍑籤缂栬緫鍔熻兘`鎸夐挳锛屽嵆鍙湅鍒癭mcp鎺ュ叆鐐筦鍔熻兘銆?

濡傛灉浣犳槸鍏ㄦā鍧楅儴缃诧紝浣跨敤绠＄悊鍛樿处鍙凤紝鐧诲綍鏅烘帶鍙帮紝鐐瑰嚮椤堕儴`鍙傛暟瀛楀吀`锛岄€夋嫨`鍙傛暟绠＄悊`鍔熻兘銆?

鐒跺悗鎼滅储鍙傛暟`server.mcp_endpoint`锛屾鏃讹紝瀹冪殑鍊煎簲璇ユ槸`null`鍊笺€?
鐐瑰嚮淇敼鎸夐挳锛屾妸涓婁竴姝ュ緱鏉ョ殑`鏅烘帶鍙癕CP鍙傛暟閰嶇疆`绮樿创鍒癭鍙傛暟鍊糮閲屻€傜劧鍚庝繚瀛樸€?

濡傛灉鑳戒繚瀛樻垚鍔燂紝璇存槑涓€鍒囬『鍒╋紝浣犲彲浠ュ幓鏅鸿兘浣撴煡鐪嬫晥鏋滀簡銆傚鏋滀笉鎴愬姛锛岃鏄庢櫤鎺у彴鏃犳硶璁块棶mcp鎺ュ叆鐐癸紝寰堝ぇ姒傜巼鏄綉缁滈槻鐏锛屾垨鑰呮病鏈夊～鍐欐纭殑灞€鍩熺綉ip銆?

# 3銆佸崟妯″潡閮ㄧ讲鏃讹紝鎬庝箞閰嶇疆MCP鎺ュ叆鐐?

濡傛灉浣犳槸鍗曟ā鍧楅儴缃诧紝鎵惧埌浣犵殑閰嶇疆鏂囦欢`data/.config.yaml`銆?
鍦ㄩ厤缃枃浠舵悳绱mcp_endpoint`锛屽鏋滄病鏈夋壘鍒帮紝浣犲氨澧炲姞`mcp_endpoint`閰嶇疆銆傜被浼兼垜鏄氨鏄繖鏍?
```
server:
  websocket: ws://浣犵殑ip鎴栬€呭煙鍚?绔彛鍙?xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# 姝ゅ鍙兘杩樻洿澶氶厤缃?.

mcp_endpoint: 浣犵殑鎺ュ叆鐐箇ebsocket鍦板潃
```
杩欐椂锛岃浣犳妸`濡備綍閮ㄧ讲MCP鎺ュ叆鐐硅繖涓湇鍔涓緱鍒扮殑`鍗曟ā鍧楅儴缃睲CP鎺ュ叆鐐筦 绮樿创鍒?`mcp_endpoint`涓€傜被浼艰繖鏍?

```
server:
  websocket: ws://浣犵殑ip鎴栬€呭煙鍚?绔彛鍙?xiaozhi/v1/
  http_port: 8002
log:
  log_level: INFO

# 姝ゅ鍙兘杩樻洿澶氶厤缃?

mcp_endpoint: ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=def
```

閰嶇疆濂藉悗锛屽惎鍔ㄥ崟妯″潡浼氳緭鍑哄涓嬬殑鏃ュ織銆?
```
250705[__main__]-INFO-鍒濆鍖栫粍浠? vad鎴愬姛 SileroVAD
250705[__main__]-INFO-鍒濆鍖栫粍浠? asr鎴愬姛 FunASRServer
250705[__main__]-INFO-OTA鎺ュ彛鏄?         http://192.168.1.25:8002/xiaozhi/ota/
250705[__main__]-INFO-瑙嗚鍒嗘瀽鎺ュ彛鏄?    http://192.168.1.25:8002/mcp/vision/explain
250705[__main__]-INFO-mcp鎺ュ叆鐐规槸        ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc
250705[__main__]-INFO-Websocket鍦板潃鏄?   ws://192.168.1.25:8000/xiaozhi/v1/
250705[__main__]-INFO-=======涓婇潰鐨勫湴鍧€鏄痺ebsocket鍗忚鍦板潃锛岃鍕跨敤娴忚鍣ㄨ闂?======
250705[__main__]-INFO-濡傛兂娴嬭瘯websocket璇风敤璋锋瓕娴忚鍣ㄦ墦寮€test鐩綍涓嬬殑test_page.html
250705[__main__]-INFO-=============================================================
```

濡備笂锛屽鏋滆兘杈撳嚭绫讳技鐨刞mcp鎺ュ叆鐐规槸`涓璥ws://192.168.1.25:8004/mcp_endpoint/mcp/?token=abc`璇存槑閰嶇疆鎴愬姛浜嗐€?



