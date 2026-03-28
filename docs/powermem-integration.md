# PowerMem 璁板繂缁勪欢闆嗘垚鎸囧崡

## 绠€浠?

[PowerMem](https://www.powermem.ai/) 鏄敱 OceanBase 寮€婧愮殑 Agent 璁板繂缁勪欢锛岄€氳繃鏈湴 LLM 杩涜璁板繂鎬荤粨鍜屾櫤鑳芥绱紝涓?AI 浠ｇ悊鎻愪緵楂樻晥鐨勮蹇嗙鐞嗗姛鑳姐€?

璐圭敤璇存槑锛歅owerMem 鏈韩寮€婧愬厤璐癸紝瀹為檯璐圭敤鍙栧喅浜庢偍閫夋嫨鐨?LLM 鍜屾暟鎹簱锛?
- 浣跨敤 SQLite + 鍏嶈垂 LLM锛堝鏅鸿氨 glm-4-flash锛? **瀹屽叏鍏嶈垂**
- 浣跨敤浜戠 LLM 鎴栦簯绔暟鎹簱 = 鎸夊搴旀湇鍔℃敹璐?

> 馃挕 **鏈€浣虫€ц兘鎻愮ず**锛歅owerMem 閰嶅悎 OceanBase 浣跨敤鍙疄鐜版渶澶ф€ц兘閲婃斁锛孲QLite 浠呭缓璁湪璧勬簮涓嶈冻鐨勬儏鍐典笅浣跨敤銆?

- **GitHub**: https://github.com/oceanbase/powermem
- **瀹樼綉**: https://www.powermem.ai/
- **浣跨敤绀轰緥**: https://github.com/oceanbase/powermem/tree/main/examples

## 鍔熻兘鐗规€?

- **鏈湴鎬荤粨**锛氶€氳繃 LLM 鍦ㄦ湰鍦拌繘琛岃蹇嗘€荤粨鍜屾彁鍙?
- **鐢ㄦ埛鐢诲儚**锛氶€氳繃 `UserMemory` 鑷姩鎻愬彇鐢ㄦ埛淇℃伅锛堝鍚嶃€佽亴涓氥€佸叴瓒ｇ瓑锛夛紝鎸佺画鏇存柊鐢ㄦ埛鐢诲儚
- **鏅鸿兘閬楀繕**锛氬熀浜庤壘瀹炬旦鏂仐蹇樻洸绾匡紝鑷姩"閬楀繕"杩囨椂鍣０淇℃伅
- **澶氱瀛樺偍鍚庣**锛氭敮鎸?OceanBase锛堟帹鑽愶紝鏈€浣虫€ц兘锛夈€丼eekDB锛堟帹鑽愶紝AI搴旂敤瀛樺偍涓€浣擄級銆丳ostgreSQL銆丼QLite锛堣交閲忓閫夛級
- **澶氱 LLM 鏀寔**锛氶€氫箟鍗冮棶銆佹櫤璋憋紙glm-4-flash 鍏嶈垂锛夈€丱penAI 绛?
- **鏅鸿兘妫€绱?*锛氬熀浜庡悜閲忔悳绱㈢殑璇箟妫€绱㈣兘鍔?
- **绉佹湁閮ㄧ讲**锛氬畬鍏ㄦ敮鎸佹湰鍦扮鏈夊寲閮ㄧ讲
- **寮傛鎿嶄綔**锛氶珮鏁堢殑寮傛璁板繂绠＄悊

## 瀹夎

PowerMem 宸叉坊鍔犲埌椤圭洰渚濊禆涓紝濡傛灉闇€瑕佹墜鍔ㄥ畨瑁咃細

```bash
pip install powermem
```

## 閰嶇疆璇存槑

### 鍩虹閰嶇疆

鍦?`config.yaml` 涓厤缃?PowerMem锛?

```yaml
selected_module:
  Memory: powermem

Memory:
  powermem:
    type: powermem
    # 鏄惁鍚敤鐢ㄦ埛鐢诲儚鍔熻兘
    # 鐢ㄦ埛鐢诲儚鏀寔: oceanbase銆乻eekdb銆乻qlite (powermem 0.3.0+)
    enable_user_profile: true
    
    # ========== LLM 閰嶇疆 ==========
    llm:
      provider: openai  # 鍙€? qwen, openai, zhipu 绛?
      config:
        api_key: 浣犵殑LLM API瀵嗛挜
        model: qwen-plus
        # openai_base_url: https://api.openai.com/v1  # 鍙€夛紝鑷畾涔夋湇鍔″湴鍧€
    
    # ========== Embedding 閰嶇疆 ==========
    embedder:
      provider: openai  # 鍙€? qwen, openai 绛?
      config:
        api_key: 浣犵殑宓屽叆妯″瀷API瀵嗛挜
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
        # embedding_dims: 1024  # 鍚戦噺缁村害锛岄潪1536鏃堕渶閰嶇疆
    
    # ========== Database 閰嶇疆 ==========
    vector_store:
      provider: sqlite  # 鍙€? oceanbase(鎺ㄨ崘), seekdb(鎺ㄨ崘), postgres, sqlite(杞婚噺)
      config: {}  # SQLite 鏃犻渶棰濆閰嶇疆
```

### 閰嶇疆鍙傛暟璇﹁В

#### LLM 閰嶇疆

| 鍙傛暟 | 璇存槑 | 鍙€夊€?|
|------|------|--------|
| `llm.provider` | LLM 鎻愪緵鍟?| `qwen`, `openai`, `zhipu` 绛?|
| `llm.config.api_key` | API 瀵嗛挜 | - |
| `llm.config.model` | 妯″瀷鍚嶇О | 鏍规嵁鎻愪緵鍟嗛€夋嫨 |
| `llm.config.openai_base_url` | 鑷畾涔夋湇鍔″湴鍧€锛堝彲閫夛級 | - |

#### Embedding 閰嶇疆

| 鍙傛暟 | 璇存槑 | 鍙€夊€?|
|------|------|--------|
| `embedder.provider` | 宓屽叆妯″瀷鎻愪緵鍟?| `qwen`, `openai` 绛?|
| `embedder.config.api_key` | API 瀵嗛挜 | - |
| `embedder.config.model` | 妯″瀷鍚嶇О | 鏍规嵁鎻愪緵鍟嗛€夋嫨 |
| `embedder.config.openai_base_url` | 鑷畾涔夋湇鍔″湴鍧€锛堝彲閫夛級 | - |

#### Database 閰嶇疆

| 鍙傛暟 | 璇存槑 | 鍙€夊€?|
|------|------|--------|
| `vector_store.provider` | 瀛樺偍鍚庣绫诲瀷 | `oceanbase`(鎺ㄨ崘), `seekdb`(鎺ㄨ崘), `postgres`, `sqlite`(杞婚噺) |
| `vector_store.config` | 鏁版嵁搴撹繛鎺ラ厤缃?| 鏍规嵁 provider 璁剧疆 |

### 璁板繂妯″紡璇存槑

PowerMem 鏀寔涓ょ璁板繂妯″紡锛?

| 妯″紡 | 閰嶇疆 | 鍔熻兘 | 瀛樺偍瑕佹眰 |
|------|------|------|----------|
| **鏅€氳蹇?* | `enable_user_profile: false` | 瀵硅瘽璁板繂瀛樺偍涓庢绱?| 鏀寔鎵€鏈夋暟鎹簱 |
| **鐢ㄦ埛鐢诲儚** | `enable_user_profile: true` | 璁板繂 + 鑷姩鎻愬彇鐢ㄦ埛鐢诲儚 | oceanbase銆乻eekdb銆乻qlite |

> 馃搶 **鐗堟湰璇存槑**锛歅owerMem 0.3.0+ 鐗堟湰锛岀敤鎴风敾鍍忓姛鑳芥敮鎸?OceanBase銆丼eekDB銆丼QLite 涓夌瀛樺偍鍚庣銆?

### 浣跨敤閫氫箟鍗冮棶锛堟帹鑽愶級

1. 璁块棶 [闃块噷浜戠櫨鐐煎钩鍙癩(https://bailian.console.aliyun.com/) 娉ㄥ唽璐﹀彿
2. 鍦?[API Key 绠＄悊](https://bailian.console.aliyun.com/?apiKey=1#/api-key) 椤甸潰鑾峰彇 API 瀵嗛挜
3. 閰嶇疆濡備笅锛?

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: qwen
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: qwen-plus
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    vector_store:
      provider: sqlite
      config: {}
```

### 浣跨敤鏅鸿氨鍏嶈垂 LLM锛堝畬鍏ㄥ厤璐规柟妗堬級

鏅鸿氨鎻愪緵鍏嶈垂鐨?glm-4-flash 妯″瀷锛岄厤鍚?SQLite 鍙疄鐜板畬鍏ㄥ厤璐逛娇鐢細

1. 璁块棶 [鏅鸿氨AI寮€鏀惧钩鍙癩(https://bigmodel.cn/) 娉ㄥ唽璐﹀彿
2. 鍦?[API Keys](https://bigmodel.cn/usercenter/proj-mgmt/apikeys) 椤甸潰鑾峰彇 API 瀵嗛挜
3. 閰嶇疆濡備笅锛?

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai  # 浣跨敤 openai 鍏煎妯″紡
      config:
        api_key: xxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx
        model: glm-4-flash
        openai_base_url: https://open.bigmodel.cn/api/paas/v4/
    embedder:
      provider: openai
      config:
        api_key: xxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxx
        model: embedding-3
        openai_base_url: https://open.bigmodel.cn/api/paas/v4/
    vector_store:
      provider: sqlite
      config: {}
```

### 浣跨敤 OpenAI

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: gpt-4o-mini
        openai_base_url: https://api.openai.com/v1
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-3-small
        openai_base_url: https://api.openai.com/v1
    vector_store:
      provider: sqlite
      config: {}
```

### 浣跨敤 OceanBase锛堟渶浣虫€ц兘鏂规锛?

OceanBase 鏄?PowerMem 鐨勬渶浣虫惌妗ｏ紝鍙疄鐜版渶澶ф€ц兘閲婃斁锛?

1. 閮ㄧ讲 OceanBase 鏁版嵁搴擄紙鏀寔寮€婧愭湰鍦伴儴缃叉垨浣跨敤浜戞湇鍔★級
   - 寮€婧愰儴缃诧細https://github.com/oceanbase/oceanbase
   - 浜戞湇鍔★細https://www.oceanbase.com/
2. 閰嶇疆濡備笅锛?

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true
    llm:
      provider: qwen
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: qwen-plus
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    vector_store:
      provider: oceanbase
      config:
        host: 127.0.0.1
        port: 2881
        user: root@test
        password: your_password
        db_name: powermem
        collection_name: memories  # 榛樿鍊?
        embedding_model_dims: 1536  # 宓屽叆鍚戦噺缁村害锛屽繀闇€鍙傛暟
```

## 璁惧璁板繂闅旂

PowerMem 浼氳嚜鍔ㄤ娇鐢ㄨ澶?ID锛坄device_id`锛変綔涓?`user_id` 杩涜璁板繂闅旂銆傝繖鎰忓懗鐫€锛?

- 姣忎釜璁惧鎷ユ湁鐙珛鐨勮蹇嗙┖闂?
- 涓嶅悓璁惧涔嬮棿鐨勮蹇嗗畬鍏ㄩ殧绂?
- 鍚屼竴璁惧鐨勫娆″璇濆彲浠ュ叡浜蹇嗕笂涓嬫枃

## 鐢ㄦ埛鐢诲儚锛圲serMemory锛?

PowerMem 鎻愪緵 `UserMemory` 绫伙紝鍙嚜鍔ㄤ粠瀵硅瘽涓彁鍙栫敤鎴风敾鍍忎俊鎭€?

> 馃搶 **鐗堟湰璇存槑**锛歅owerMem 0.3.0+ 鐗堟湰锛岀敤鎴风敾鍍忓姛鑳芥敮鎸?OceanBase銆丼eekDB銆丼QLite 涓夌瀛樺偍鍚庣銆?

### 鍚敤鐢ㄦ埛鐢诲儚

鍦ㄩ厤缃腑璁剧疆 `enable_user_profile: true` 鍗冲彲鍚敤锛?

```yaml
Memory:
  powermem:
    type: powermem
    enable_user_profile: true  # 鍚敤鐢ㄦ埛鐢诲儚
    llm:
      provider: qwen
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: qwen-plus
    embedder:
      provider: openai
      config:
        api_key: sk-xxxxxxxxxxxxxxxx
        model: text-embedding-v4
        openai_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    vector_store:
      provider: sqlite  # 鐢ㄦ埛鐢诲儚鏀寔: oceanbase銆乻eekdb銆乻qlite
      config: {}
```

### 鐢ㄦ埛鐢诲儚鑳藉姏

| 鑳藉姏 | 璇存槑 |
|------|------|
| **淇℃伅鎻愬彇** | 鑷姩浠庡璇濅腑鎻愬彇濮撳悕銆佸勾榫勩€佽亴涓氥€佸叴瓒ｇ瓑 |
| **鎸佺画鏇存柊** | 闅忕潃瀵硅瘽杩涜锛屼笉鏂畬鍠勭敤鎴风敾鍍?|
| **鐢诲儚妫€绱?* | 灏嗙敤鎴风敾鍍忎笌璁板繂鎼滅储缁撳悎锛屾彁鍗囨绱㈢浉鍏虫€?|
| **鏅鸿兘閬楀繕** | 鍩轰簬鑹惧娴╂柉閬楀繕鏇茬嚎锛屾贰鍖栬繃鏃朵俊鎭?|

### 宸ヤ綔鍘熺悊

鍚敤鐢ㄦ埛鐢诲儚鍚庯紝灏忔櫤鍦ㄦ煡璇㈣蹇嗘椂浼氳嚜鍔ㄨ繑鍥烇細
1. **鐢ㄦ埛鐢诲儚**锛氱敤鎴风殑鍩烘湰淇℃伅銆佸叴瓒ｇ埍濂界瓑
2. **鐩稿叧璁板繂**锛氫笌褰撳墠瀵硅瘽鐩稿叧鐨勫巻鍙茶蹇?

> 鉁?**鐗堟湰璇存槑**锛歅owerMem 0.3.0+ 鐗堟湰锛岀敤鎴风敾鍍忓姛鑳芥敮鎸?OceanBase銆丼eekDB銆丼QLite 涓夌瀛樺偍鍚庣銆?

## 涓庡叾浠栬蹇嗙粍浠剁殑瀵规瘮

| 鐗规€?| PowerMem | mem0ai | mem_local_short |
|------|----------|--------|-----------------|
| 宸ヤ綔鏂瑰紡 | 鏈湴鎬荤粨 | 浜戠鎺ュ彛 | 鏈湴鎬荤粨 |
| 瀛樺偍浣嶇疆 | 鏈湴/浜戠DB | 浜戠 | 鏈湴YAML |
| 璐圭敤 | 鍙栧喅浜嶭LM鍜孌B | 1000娆?鏈堝厤璐?| 瀹屽叏鍏嶈垂 |
| 鏅鸿兘妫€绱?| 鉁?鍚戦噺鎼滅储 | 鉁?鍚戦噺鎼滅储 | 鉂?鍏ㄩ噺杩斿洖 |
| 鐢ㄦ埛鐢诲儚 | 鉁?UserMemory | 鉂?| 鉂?|
| 鏅鸿兘閬楀繕 | 鉁?閬楀繕鏇茬嚎 | 鉂?| 鉂?|
| 绉佹湁閮ㄧ讲 | 鉁?鏀寔 | 鉂?浠呬簯绔?| 鉁?鏀寔 |
| 鏁版嵁搴撴敮鎸?| OceanBase(鎺ㄨ崘)/SeekDB/PostgreSQL/SQLite | - | YAML 鏂囦欢 |

## 甯歌闂

### 1. API 瀵嗛挜閿欒

濡傛灉鍑虹幇 `API key is required` 閿欒锛岃妫€鏌ワ細
- `llm_api_key` 鍜?`embedding_api_key` 鏄惁姝ｇ‘濉啓
- API 瀵嗛挜鏄惁鏈夋晥

### 2. 妯″瀷涓嶅瓨鍦?

濡傛灉鍑虹幇妯″瀷涓嶅瓨鍦ㄧ殑閿欒锛岃纭锛?
- `llm_model` 鍜?`embedding_model` 鍚嶇О鏄惁姝ｇ‘
- 瀵瑰簲鐨勬ā鍨嬫湇鍔℃槸鍚﹀凡寮€閫?

### 3. 杩炴帴瓒呮椂

濡傛灉鍑虹幇杩炴帴瓒呮椂锛屽彲浠ュ皾璇曪細
- 妫€鏌ョ綉缁滆繛鎺?
- 濡傛灉浣跨敤浠ｇ悊锛岄厤缃?`llm_base_url` 鍜?`embedding_base_url`

## 娴嬭瘯楠岃瘉

鍙互鍦ㄨ櫄鎷熺幆澧冧腑娴嬭瘯 PowerMem 鏄惁姝ｅ父宸ヤ綔锛?

```bash
# 婵€娲昏櫄鎷熺幆澧?
source .venv/bin/activate

# 娴嬭瘯 PowerMem 瀵煎叆
python -c "from powermem import AsyncMemory; print('PowerMem 瀵煎叆鎴愬姛')"

# 娴嬭瘯 UserMemory 瀵煎叆锛堢敤鎴风敾鍍忓姛鑳斤級
python -c "from powermem import UserMemory; print('UserMemory 瀵煎叆鎴愬姛')"
```

## 鏇村璧勬簮

- [PowerMem 瀹樻柟鏂囨。](https://www.powermem.ai/)
- [PowerMem GitHub 浠撳簱](https://github.com/oceanbase/powermem)
- [PowerMem 浣跨敤绀轰緥](https://github.com/oceanbase/powermem/tree/main/examples)
- [OceanBase 瀹樼綉](https://www.oceanbase.com/)
- [OceanBase GitHub](https://github.com/oceanbase/oceanbase)
- [SeekDB GitHub](https://github.com/oceanbase/seekdb)锛圓I鍘熺敓鎼滅储鏁版嵁搴擄級
- [闃块噷浜戠櫨鐐煎钩鍙癩(https://bailian.console.aliyun.com/)



