# IndexStreamTTS 浣跨敤鎸囧崡

## 鐜鍑嗗
### 1. 鍏嬮殕椤圭洰 
```bash 
git clone https://github.com/Ksuriuri/index-tts-vllm.git
```
杩涘叆瑙ｅ帇鍚庣殑鐩綍
```bash
cd index-tts-vllm
```
鍒囨崲鍒版寚瀹氱増鏈?(浣跨敤VLLM-0.10.2鐨勫巻鍙茬増鏈?
```bash
git checkout 224e8d5e5c8f66801845c66b30fa765328fd0be3
```

### 2. 鍒涘缓骞舵縺娲?conda 鐜
```bash 
conda create -n index-tts-vllm python=3.12
conda activate index-tts-vllm
```

### 3. 瀹夎PyTorch 闇€瑕佺増鏈负2.8.0锛堟渶鏂扮増锛?
#### 鏌ョ湅鏄惧崱鏈€楂樻敮鎸佺殑鐗堟湰鍜屽疄闄呭畨瑁呯殑鐗堟湰
```bash
nvidia-smi
nvcc --version
``` 
#### 椹卞姩鏀寔鐨勬渶楂?CUDA 鐗堟湰
```bash
CUDA Version: 12.8
```
#### 瀹為檯瀹夎鐨?CUDA 缂栬瘧鍣ㄧ増鏈?
```bash
Cuda compilation tools, release 12.8, V12.8.89
```
#### 閭ｄ箞瀵瑰簲鐨勫畨瑁呭懡浠わ紙pytorch榛樿缁欑殑鏄?2.8鐨勯┍鍔ㄧ増鏈級
```bash
pip install torch torchvision
```
闇€瑕?pytorch 鐗堟湰 2.8.0锛堝搴?vllm 0.10.2锛夛紝鍏蜂綋瀹夎鎸囦护璇峰弬鑰冿細[pytorch 瀹樼綉](https://pytorch.org/get-started/locally/)

### 4. 瀹夎渚濊禆
```bash 
pip install -r requirements.txt
```

### 5. 涓嬭浇妯″瀷鏉冮噸
### 鏂规涓€锛氫笅杞藉畼鏂规潈閲嶆枃浠跺悗杞崲
姝や负瀹樻柟鏉冮噸鏂囦欢锛屼笅杞藉埌鏈湴浠绘剰璺緞鍗冲彲锛屾敮鎸?IndexTTS-1.5 鐨勬潈閲? 
| HuggingFace                                                   | ModelScope                                                          |
|---------------------------------------------------------------|---------------------------------------------------------------------|
| [IndexTTS](https://huggingface.co/IndexTeam/Index-TTS)        | [IndexTTS](https://modelscope.cn/models/IndexTeam/Index-TTS)        |
| [IndexTTS-1.5](https://huggingface.co/IndexTeam/IndexTTS-1.5) | [IndexTTS-1.5](https://modelscope.cn/models/IndexTeam/IndexTTS-1.5) |

涓嬮潰浠odelScope鐨勫畨瑁呮柟娉曚负渚? 
#### 璇锋敞鎰忥細git闇€瑕佸畨瑁呭苟鍒濆鍖栧惎鐢╨fs锛堝宸插畨瑁呭彲浠ヨ烦杩囷級
```bash
sudo apt-get install git-lfs
git lfs install
```
鍒涘缓妯″瀷鐩綍锛屽苟鎷夊彇妯″瀷
```bash 
mkdir model_dir
cd model_dir
git clone https://www.modelscope.cn/IndexTeam/IndexTTS-1.5.git
```

#### 妯″瀷鏉冮噸杞崲
```bash 
bash convert_hf_format.sh /path/to/your/model_dir
```
渚嬪锛氫綘涓嬭浇鐨処ndexTTS-1.5妯″瀷瀛樻斁鍦╩odel_dir鐩綍涓嬶紝鍒欐墽琛屼互涓嬪懡浠?
```bash
bash convert_hf_format.sh model_dir/IndexTTS-1.5
```
姝ゆ搷浣滀細灏嗗畼鏂圭殑妯″瀷鏉冮噸杞崲涓?transformers 搴撳吋瀹圭殑鐗堟湰锛屼繚瀛樺湪妯″瀷鏉冮噸璺緞涓嬬殑 vllm 鏂囦欢澶逛腑锛屾柟渚垮悗缁?vllm 搴撳姞杞芥ā鍨嬫潈閲?

### 6. 鏇存敼鎺ュ彛閫傞厤涓€涓嬮」鐩?
鎺ュ彛杩斿洖鏁版嵁涓庨」鐩笉閫傞厤闇€瑕佽皟鏁翠竴涓嬶紝浣垮叾鐩存帴杩斿洖闊抽鏁版嵁
```bash
vi api_server.py
```
```bash 
@app.post("/tts", responses={
    200: {"content": {"application/octet-stream": {}}},
    500: {"content": {"application/json": {}}}
})
async def tts_api(request: Request):
    try:
        data = await request.json()
        text = data["text"]
        character = data["character"]

        global tts
        sr, wav = await tts.infer_with_ref_audio_embed(character, text)

        return Response(content=wav.tobytes(), media_type="application/octet-stream")
        
    except Exception as ex:
        tb_str = ''.join(traceback.format_exception(type(ex), ex, ex.__traceback__))
        print(tb_str)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(tb_str)
            }
        )
```

### 7.缂栧啓sh鍚姩鑴氭湰锛堣娉ㄦ剰瑕佸湪鐩稿簲鐨刢onda鐜涓嬭繍琛岋級
```bash 
vi start_api.sh
```
### 灏嗕笅闈㈠唴瀹圭矘璐磋繘鍘诲苟鎸?杈撳叆wq淇濆瓨  
#### 鑴氭湰涓殑/home/system/index-tts-vllm/model_dir/IndexTTS-1.5 璇疯嚜琛屼慨鏀逛负瀹為檯璺緞
```bash
# 婵€娲籧onda鐜
conda activate index-tts-vllm 
echo "婵€娲婚」鐩甤onda鐜"
sleep 2
# 鏌ユ壘鍗犵敤11996绔彛鐨勮繘绋嬪彿
PID_VLLM=$(sudo netstat -tulnp | grep 11996 | awk '{print $7}' | cut -d'/' -f1)

# 妫€鏌ユ槸鍚︽壘鍒拌繘绋嬪彿
if [ -z "$PID_VLLM" ]; then
  echo "娌℃湁鎵惧埌鍗犵敤11996绔彛鐨勮繘绋?
else
  echo "鎵惧埌鍗犵敤11996绔彛鐨勮繘绋嬶紝杩涚▼鍙蜂负: $PID_VLLM"
  # 鍏堝皾璇曟櫘閫歬ill锛岀瓑寰?绉?
  kill $PID_VLLM
  sleep 2
  # 妫€鏌ヨ繘绋嬫槸鍚﹁繕鍦?
  if ps -p $PID_VLLM > /dev/null; then
    echo "杩涚▼浠嶅湪杩愯锛屽己鍒剁粓姝?.."
    kill -9 $PID_VLLM
  fi
  echo "宸茬粓姝㈣繘绋?$PID_VLLM"
fi

# 鏌ユ壘鍗犵敤VLLM::EngineCore杩涚▼
GPU_PIDS=$(ps aux | grep -E "VLLM|EngineCore" | grep -v grep | awk '{print $2}')

# 妫€鏌ユ槸鍚︽壘鍒拌繘绋嬪彿
if [ -z "$GPU_PIDS" ]; then
  echo "娌℃湁鎵惧埌VLLM鐩稿叧杩涚▼"
else
  echo "鎵惧埌VLLM鐩稿叧杩涚▼锛岃繘绋嬪彿涓? $GPU_PIDS"
  # 鍏堝皾璇曟櫘閫歬ill锛岀瓑寰?绉?
  kill $GPU_PIDS
  sleep 2
  # 妫€鏌ヨ繘绋嬫槸鍚﹁繕鍦?
  if ps -p $GPU_PIDS > /dev/null; then
    echo "杩涚▼浠嶅湪杩愯锛屽己鍒剁粓姝?.."
    kill -9 $GPU_PIDS
  fi
  echo "宸茬粓姝㈣繘绋?$GPU_PIDS"
fi

# 鍒涘缓tmp鐩綍锛堝鏋滀笉瀛樺湪锛?
mkdir -p tmp

# 鍚庡彴杩愯api_server.py锛屾棩蹇楅噸瀹氬悜鍒皌mp/server.log
nohup python api_server.py --model_dir /home/system/index-tts-vllm/model_dir/IndexTTS-1.5 --port 11996 > tmp/server.log 2>&1 &
echo "api_server.py 宸插湪鍚庡彴杩愯锛屾棩蹇楄鏌ョ湅 tmp/server.log"
```
缁欒剼鏈墽琛屾潈闄愬苟杩愯鑴氭湰
```bash 
chmod +x start_api.sh
./start_api.sh
```
鏃ュ織浼氬湪tmp/server.log涓緭鍑猴紝鍙互閫氳繃浠ヤ笅鍛戒护鏌ョ湅鏃ュ織鎯呭喌
```bash
tail -f tmp/server.log
```
濡傛灉鏄惧崱鍐呭瓨瓒冲锛屽彲鍦ㄨ剼鏈腑娣诲姞鍚姩鍙傛暟 ----gpu_memory_utilization 鏉ヨ皟鏁存樉瀛樺崰鐢ㄦ瘮渚嬶紝榛樿鍊间负 0.25

## 闊宠壊閰嶇疆
index-tts-vllm鏀寔閫氳繃閰嶇疆鏂囦欢娉ㄥ唽鑷畾涔夐煶鑹诧紝鏀寔鍗曢煶鑹插拰娣峰悎闊宠壊閰嶇疆銆? 
鍦ㄩ」鐩牴鐩綍涓嬬殑assets/speaker.json鏂囦欢涓厤缃嚜瀹氫箟闊宠壊
### 閰嶇疆鏍煎紡璇存槑
```bash
{
    "璇磋瘽浜哄悕绉?": [
        "闊抽鏂囦欢璺緞1.wav",
        "闊抽鏂囦欢璺緞2.wav"
    ],
    "璇磋瘽浜哄悕绉?": [
        "闊抽鏂囦欢璺緞3.wav"
    ]
}
```
### 娉ㄦ剰 锛堥厤缃鑹插悗闇€閲嶅惎鏈嶅姟杩涜闊宠壊娉ㄥ唽锛?
娣诲姞鍚庨渶鍦ㄦ櫤鎺у彴涓坊鍔犵浉搴旂殑璇磋瘽浜猴紙鍗曟ā鍧楀垯鏇存崲鐩稿簲鐨剉oice锛

