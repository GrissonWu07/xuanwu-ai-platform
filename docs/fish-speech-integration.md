鐧诲綍AutoDL锛岀璧侀暅鍍?
閫夋嫨闀滃儚:
```
PyTorch / 2.1.0 / 3.10(ubuntu22.04) / cuda 12.1
```

鏈哄櫒寮€鏈哄悗锛岃缃鏈姞閫?
```
source /etc/network_turbo
```

杩涘叆宸ヤ綔鐩綍
```
cd autodl-tmp/
```

鎷夊彇椤圭洰
```
git clone https://gitclone.com/github.com/fishaudio/fish-speech.git ; cd fish-speech
```

瀹夎渚濊禆
```
pip install -e.
```

濡傛灉鎶ラ敊锛屽畨瑁卲ortaudio
```
apt-get install portaudio19-dev -y
```

瀹夎鍚庢墽琛?
```
pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121
```

涓嬭浇妯″瀷
```
cd tools
python download_models.py 
```

涓嬭浇瀹屾ā鍨嬪悗杩愯鎺ュ彛
```
python -m tools.api_server --listen 0.0.0.0:6006 
```

鐒跺悗鐢ㄦ祻瑙堝櫒鍘诲埌aotodl瀹炰緥椤甸潰
```
https://autodl.com/console/instance/list
```

濡備笅鍥剧偣鍑讳綘鍒氭墠鏈哄櫒鐨刞鑷畾涔夋湇鍔鎸夐挳锛屽紑鍚鍙ｈ浆鍙戞湇鍔?
![鑷畾涔夋湇鍔(images/fishspeech/autodl-01.png)

绔彛杞彂鏈嶅姟璁剧疆瀹屾垚鍚庯紝浣犳湰鍦扮數鑴戞墦寮€缃戝潃`http://localhost:6006/`锛屽氨鍙互璁块棶fish-speech鐨勬帴鍙ｄ簡
![鏈嶅姟棰勮](images/fishspeech/autodl-02.png)


濡傛灉浣犳槸鍗曟ā鍧楅儴缃诧紝鏍稿績閰嶇疆濡備笅
```
selected_module:
  TTS: FishSpeech
TTS:
  FishSpeech:
    reference_audio: ["config/assets/wakeup_words.wav",]
    reference_text: ["鍝堝暟鍟婏紝鎴戞槸灏忔櫤鍟︼紝澹伴煶濂藉惉鐨勫彴婀惧コ瀛╀竴鏋氾紝瓒呭紑蹇冭璇嗕綘鑰讹紝鏈€杩戝湪蹇欏暐锛屽埆蹇樹簡缁欐垜鏉ョ偣鏈夎叮鐨勬枡鍝︼紝鎴戣秴鐖卞惉鍏崷鐨勫暒",]
    api_key: "123"
    api_url: "http://127.0.0.1:6006/v1/tts"
```

鐒跺悗閲嶅惎鏈嶅姟

