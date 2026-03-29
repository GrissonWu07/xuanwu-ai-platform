# AtlasClaw 涓诲璇濆紩鎿庝笓椤硅璁℃枃妗?

## 1. 鏂囨。鐩殑

鏈枃妗ｅ畾涔?`xuanwu-server` 涓?`AtlasClaw` 鐨勯噸鏋勭洰鏍囨灦鏋勶紝骞舵槑纭湰娆￠噸鏋勭殑鏍稿績鍐崇瓥锛?

- `AtlasClaw` 鎴愪负鍞竴涓诲璇濆紩鎿?
- `xuanwu-server` 淇濈暀涓鸿澶囨帴鍏ヤ笌鎵ц灞?
- 褰撳墠鏈湴 `LLM`銆乣Intent`銆乣Memory` 涓嶅啀鎵挎媴涓诲璇濊亴璐?
- 璁惧鏈湴鑳藉姏閫氳繃杩愯鏃?API 鏆撮湶缁?`AtlasClaw`锛岀敱 `AtlasClaw` 缁熶竴瑙勫垝涓庤皟搴?

鏈枃妗ｆ槸鍚庣画瀹炵幇銆佹帴鍙ｈ仈璋冦€佹ā鍧椾笅绾垮拰娴嬭瘯楠屾敹鐨勫敮涓€璁捐渚濇嵁銆?

## 2. 鑳屾櫙涓庨棶棰?

褰撳墠椤圭洰涓紝`xuanwu-server` 鍚屾椂鎵挎媴浜嗕互涓嬭亴璐ｏ細

- 璁惧 WebSocket 鎺ュ叆
- 闊抽杈撳叆杈撳嚭涓庢祦鎺?
- ASR / TTS
- 鏈湴鎰忓浘璇嗗埆
- 鏈湴 LLM 鍥炲鐢熸垚
- 鏈湴宸ュ叿璋冨害
- 璁板繂涓庝笂涓嬫枃澶勭悊

杩欑璁捐鐨勯棶棰樻槸锛?

- 璁惧鎺ュ叆閫昏緫涓庡璇濇櫤鑳藉己鑰﹀悎锛宍core/connection.py` 杩囬噸
- 鏈湴 `Intent`銆乣LLM`銆乣Memory`銆佸伐鍏锋墽琛屾祦绋嬩氦缁囷紝鎵╁睍鍜屾浛鎹㈡垚鏈珮
- 寰堥毦澶嶇敤 `AtlasClaw` 宸插叿澶囩殑浼氳瘽銆丄gent銆乀ool銆丼kill銆丮emory 鑳藉姏
- 涓诲璇濋摼璺棤娉曞崌绾т负鐪熸鐨勬櫤鑳戒唬鐞嗘ā寮?

鏈閲嶆瀯鐨勭洰鏍囦笉鏄皢 `AtlasClaw` 浣滀负鏅€?LLM 鎻愪緵鏂规帴鍏ワ紝鑰屾槸灏嗗叾鎻愬崌涓烘暣涓郴缁熺殑鍞竴涓诲璇濆紩鎿庛€?

## 3. 璁捐鐩爣

### 3.1 鏍稿績鐩爣

- 璁惧杩炴帴銆侀煶棰戦噰闆嗐€乀TS 鎾斁浠嶇敱 `xuanwu-server` 璐熻矗
- 鐢ㄦ埛鏂囨湰涓€鏃﹀舰鎴愶紝鍗崇敱 `AtlasClaw` 璐熻矗涓诲璇濄€佷换鍔¤鍒掋€佸伐鍏烽€夋嫨鍜岃蹇嗙鐞?
- 鎵€鏈夊鏉傝涔変唬鐞嗚涓虹粺涓€鏀舵暃鍒?`AtlasClaw`
- `xuanwu-server` 鍙仛杩愯鏃舵墽琛屻€佸崗璁浆鎹㈠拰瀹炴椂鎺у埗

### 3.2 闈炵洰鏍?

- 鏈樁娈典笉閲嶅啓 Web 绠＄悊鍙版垨绉诲姩绔?
- 鏈樁娈典笉灏?`AtlasClaw` 鍐呭祵鍒?`xuanwu-server` 杩涚▼鍐?
- 鏈樁娈典笉淇濈暀鈥滃弻涓诲紩鎿庘€濋暱鏈熷苟琛屾ā寮?
- 鏈樁娈典笉閲嶆柊璁捐璁惧鍗忚

## 4. 鎬讳綋鏋舵瀯

### 4.1 閲嶆瀯鍚庣殑鑱岃矗杈圭晫

`xuanwu-server` 璐熻矗锛?

- 璁惧鍗忚鎺ュ叆
- WebSocket / HTTP / OTA / MQTT
- VAD / ASR / TTS / 闊抽娴佹帶
- 璁惧杩炴帴鐘舵€?
- `hello` / `ping` / `abort` / `listen` / `server` 绛夎澶囨帶鍒舵秷鎭?
- 璁惧鏈湴宸ュ叿鎵ц
- 涓?`AtlasClaw` 鎻愪緵杩愯鏃惰兘鍔?API

`AtlasClaw` 璐熻矗锛?

- 涓讳細璇濈鐞?
- 涓诲璇濈敓鎴?
- 鎰忓浘璇嗗埆涓庝换鍔¤鍒?
- Tool / Skill / Provider 璋冨害
- 璁板繂涓庝笂涓嬫枃缂栨帓
- 澶氭浠ｇ悊鎺ㄧ悊
- 鏈€缁堝洖澶嶆祦鐢熸垚

### 4.2 鐩爣璋冪敤閾?

```mermaid
sequenceDiagram
    participant Device as Device/ESP32
    participant XZ as xuanwu-server
    participant AC as AtlasClaw

    Device->>XZ: audio / hello / ping / abort
    XZ->>XZ: VAD + ASR + session binding
    XZ->>AC: POST /agent/run
    XZ->>AC: GET /agent/runs/{run_id}/stream
    AC-->>XZ: SSE assistant/tool/thinking/lifecycle/error
    AC->>XZ: POST /runtime/v1/sessions/{id}/tool-executions
    XZ-->>AC: tool result
    XZ->>XZ: TTS + audio rate control
    XZ-->>Device: stt / tts / audio packets
```

## 5. 褰撳墠浠ｇ爜鐜扮姸涓庢浛鎹㈢偣

### 5.1 褰撳墠涓诲璇濋摼璺?

褰撳墠 `xuanwu-server` 鐨勪富瀵硅瘽閾捐矾涓昏浣嶄簬浠ヤ笅鏂囦欢锛?

- `main/xuanwu-server/core/handle/receiveAudioHandle.py`
- `main/xuanwu-server/core/handle/intentHandler.py`
- `main/xuanwu-server/core/connection.py`
- `main/xuanwu-server/core/utils/modules_initialize.py`
- `main/xuanwu-server/core/providers/tools/unified_tool_handler.py`

褰撳墠娴佺▼澶ц嚧涓猴細

1. 璁惧涓婁紶闊抽
2. 鏈湴 `VAD` 鍒ゆ柇璇磋瘽鐘舵€?
3. 鏈湴 `ASR` 浜у嚭鏂囨湰
4. `receiveAudioHandle.startToChat()` 鍚姩瀵硅瘽
5. `intentHandler.handle_user_intent()` 鍐冲畾鏄惁鍛戒腑鎰忓浘涓庡嚱鏁拌皟鐢?
6. 鑻ユ湭鍛戒腑锛屽垯 `conn.chat()` 浣跨敤鏈湴 `LLM` 鐢熸垚鍥炲
7. 鏈湴宸ュ叿鐢?`UnifiedToolHandler` 鎵ц
8. 鏈湴 `TTS` 杞闊宠繑鍥炶澶?

### 5.2 鏈閲嶆瀯鍚庣殑涓绘浛鎹㈢偣

浠ヤ笅閫昏緫灏嗕粠鏈湴涓昏矾寰勪腑绉诲嚭锛?

- 涓诲洖澶嶇敓鎴?
- 涓绘剰鍥捐瘑鍒?
- 涓昏蹇嗙鐞?
- 涓诲伐鍏疯鍒?

浠ヤ笅閫昏緫淇濈暀鍦ㄦ湰鍦帮細

- 闊抽澶勭悊
- 璁惧鐘舵€佹帶鍒?
- 瀹炴椂涓柇
- TTS 杈撳嚭
- 璁惧鏈湴鑳藉姏鎵ц

## 6. 鍏抽敭璁捐鍐崇瓥

### 6.1 AtlasClaw 鏄敮涓€涓诲璇濆紩鎿?

榛樿鎯呭喌涓嬶細

- 鎵€鏈夌敤鎴疯嚜鐒惰瑷€杈撳叆鍧囧彂閫佸埌 `AtlasClaw`
- 鏈湴 `Intent` 涓嶅弬涓庝富鍐崇瓥
- 鏈湴 `LLM` 涓嶇敓鎴愪富鍥炲
- 鏈湴 `Memory` 涓嶇淮鎶や富浼氳瘽鐘舵€?

鏈湴缁勪欢浠呬繚鐣欎袱绉嶇敤閫旓細

- 璁惧绾у嵆鏃舵帶鍒?
- 绱ф€?fallback

### 6.2 `AtlasClaw` 涓嶄綔涓?LLM Provider 闆嗘垚

鏈涓嶅皢 `AtlasClaw` 濉炲叆 `core/providers/llm/*`銆?

鍘熷洜锛?

- `AtlasClaw` 鏄?Agent 骞冲彴锛屼笉鏄崟绾ā鍨嬭皟鐢ㄦ柟
- 瀹冩湁浼氳瘽銆佸伐鍏枫€佹妧鑳姐€佷笂涓嬫枃銆丼SE 浜嬩欢娴佺瓑鏇撮珮灞傝涔?
- 鎶婂畠灏佽鎴愭櫘閫?LLM provider 浼氫涪澶卞伐鍏蜂簨浠躲€佹€濊€冮樁娈点€佷細璇濇帶鍒惰兘鍔?

鍥犳搴旀柊澧?`DialogueEngine` 鎶借薄锛屽苟瀹炵幇 `AtlasClawDialogueEngine`銆?

### 6.3 璁惧鏄細璇濅富浣?

`AtlasClaw` 榛樿鐨?`/sessions` 璁捐鍋忓悜鈥滆璇佺敤鎴蜂綔涓轰細璇濅富浣撯€濓紝杩欎笌璁惧鍨嬪満鏅笉瀹屽叏涓€鑷淬€?

鍥犳鏈璁捐閲囩敤锛?

- `xuanwu-server` 鑷鏋勯€犵ǔ瀹氱殑 `session_key`
- 鐩存帴璋冪敤 `AtlasClaw /agent/run`
- 涓嶄緷璧?`AtlasClaw /sessions` 鎺ュ彛鏉ュ垎閰嶄細璇濊韩浠?

## 7. 浼氳瘽涓庤韩浠芥ā鍨?

### 7.1 浼氳瘽涓讳綋

鏈璁′腑浼氳瘽涓讳綋鏄€滆澶囪繛鎺モ€濊€屼笉鏄祻瑙堝櫒鐢ㄦ埛銆?

瀹氫箟濡備笅锛?

- `device_id`锛氳澶囨爣璇嗭紝涓讳細璇濅富浣?
- `client_id`锛氬崟璁惧涓嬬殑杩炴帴瀹炰緥鏍囪瘑
- `runtime_session_id`锛歚xuanwu-server` 鏈湴浼氳瘽 ID
- `atlas_session_key`锛氬彂缁?`AtlasClaw` 鐨勭ǔ瀹氫細璇濋敭

### 7.2 `atlas_session_key` 瑙勮寖

鎺ㄨ崘瑙勮寖濡備笅锛?

- 鍗曡澶囧崟浼氳瘽锛?
  - `agent:main:user:device-{device_id}:xuanwu:dm:{device_id}`
- 鍗曡澶囧骞跺彂杩炴帴锛?
  - `agent:main:user:device-{device_id}:xuanwu:dm:{device_id}:topic:{client_id}`

瑙勫垯锛?

- `agent_id` 鍥哄畾涓?`main`
- `user_id` 鍥哄畾鏄犲皠涓?`device-{device_id}`
- `channel` 鍥哄畾涓?`xuanwu`
- `peer_id` 鍥哄畾涓?`device_id`
- 濡傞渶骞跺彂闅旂锛屼娇鐢?`topic:{client_id}`

### 7.3 鏈湴杩愯鏃朵細璇濇敞鍐岃〃

`xuanwu-server` 闇€瑕佹柊澧炶繍琛屾椂娉ㄥ唽琛細

- `runtime_session_id -> websocket connection`
- `runtime_session_id -> device_id`
- `runtime_session_id -> client_id`
- `runtime_session_id -> atlas_session_key`
- `atlas_session_key -> current runtime session`

寤鸿鏂板妯″潡锛?

- `main/xuanwu-server/core/runtime/session_registry.py`

寤鸿鎺ュ彛锛?

```python
class RuntimeSessionRegistry:
    def register(self, runtime_session_id: str, device_id: str, client_id: str, atlas_session_key: str, conn) -> None: ...
    def unregister(self, runtime_session_id: str) -> None: ...
    def get_by_runtime_session(self, runtime_session_id: str): ...
    def get_by_atlas_session(self, atlas_session_key: str): ...
```

## 8. AtlasClaw 瀵规帴鎺ュ彛璁捐

### 8.1 鎺ュ彛閫夋嫨

鏈璁′娇鐢?`AtlasClaw` 鐜版湁 API锛?

- `POST /agent/run`
- `GET /agent/runs/{run_id}/stream`
- `POST /agent/runs/{run_id}/abort`

涓嶄綔涓轰富璺緞浣跨敤锛?

- `POST /sessions`
- `GET /sessions/{session_key}`

### 8.2 `AgentRunRequest` 鎵╁睍

褰撳墠 `AtlasClaw` 鐨?`AgentRunRequest` 瀛楁鏄細

- `session_key`
- `message`
- `model`
- `timeout_seconds`

鏈闇€瑕佹墿灞?`context` 瀛楁锛?

```json
{
  "session_key": "agent:main:user:device-esp32-001:xuanwu:dm:esp32-001",
  "message": "甯垜鐪嬩竴涓嬬獥澶栧ぉ姘?,
  "timeout_seconds": 120,
  "context": {
    "device_id": "esp32-001",
    "client_id": "client-001",
    "runtime_session_id": "rt-123",
    "channel": "xuanwu",
    "bind_status": "bound",
    "locale": "zh-CN",
    "audio_format": "opus",
    "capabilities": {
      "speaker": true,
      "camera": true,
      "mcp": true,
      "iot": true
    },
    "device_metadata": {
      "firmware_version": "1.0.0",
      "sample_rate": 24000
    }
  }
}
```

### 8.3 `context` 瀛楁琛?

| 瀛楁 | 绫诲瀷 | 蹇呭～ | 璇存槑 |
|---|---|---:|---|
| `device_id` | string | 鏄?| 璁惧 ID |
| `client_id` | string | 鍚?| 褰撳墠杩炴帴瀹炰緥 ID |
| `runtime_session_id` | string | 鏄?| `xuanwu-server` 鏈湴杩愯鏃朵細璇?ID |
| `channel` | string | 鏄?| 鍥哄畾涓?`xuanwu` |
| `bind_status` | string | 鏄?| `bound` / `pending` / `unknown` |
| `locale` | string | 鍚?| 浼氳瘽璇█鍋忓ソ |
| `audio_format` | string | 鍚?| 璁惧闊抽缂栫爜 |
| `capabilities` | object | 鏄?| 璁惧鑳藉姏澹版槑 |
| `device_metadata` | object | 鍚?| 鍥轰欢銆佸瀷鍙枫€侀噰鏍风巼绛?|

### 8.4 AtlasClaw SSE 浜嬩欢璇箟

淇濈暀 `AtlasClaw` 鐜版湁 SSE 浜嬩欢锛?

- `lifecycle`
- `assistant`
- `tool`
- `thinking`
- `error`

鍏朵腑鏄犲皠瑙勫垯濡備笅锛?

| AtlasClaw 浜嬩欢 | xuanwu-server 琛屼负 |
|---|---|
| `lifecycle:start` | 鏍囪杩滅瀵硅瘽寮€濮?|
| `thinking:start` | 鍙€夊彂閫佲€滄€濊€冧腑鈥濆唴閮ㄧ姸鎬侊紝涓嶆挱鎶?|
| `assistant` | 鑱氬悎鏂囨湰鐗囨锛岃浆涓?TTS 杈撳嚭 |
| `tool:start` | 鍙€夎褰曟棩蹇楁垨鍙戦€佽交閲忕姸鎬?|
| `tool:end` | 鏇存柊鍐呴儴鐘舵€侊紝涓嶇洿鎺ユ挱鎶?|
| `error` | 杩涘叆閿欒鍥炲绛栫暐 |
| `lifecycle:end` | 缁撴潫褰撳墠瀵硅瘽杞 |

### 8.5 娴佸紡杈撳嚭绛栫暐

鏈湴 TTS 浠嶇劧缁存寔鐜版湁娴佸紡杈撳嚭妯″瀷銆?

绾﹀畾锛?

- `assistant` 浜嬩欢鍐呭鎸夊閲忔枃鏈鐞?
- `xuanwu-server` 瀵瑰閲忔枃鏈仛鍙ヨ竟鐣岀紦鍐?
- 姣忓埌鍙ュ瓙绾ф柇鐐瑰嵆鍠傜粰 TTS
- `lifecycle:end` 鏃跺啿鍒峰墿浣欐枃鏈?

鍥犳闇€瑕佹柊澧炴湰鍦扮粍浠讹細

- `AtlasClawStreamBridge`

寤鸿浣嶇疆锛?

- `main/xuanwu-server/core/providers/agent/atlasclaw_stream_bridge.py`

## 9. xuanwu-server 杩愯鏃?API 璁捐

`AtlasClaw` 浣滀负涓诲紩鎿庡悗锛岄渶瑕佸洖璋冭澶囨湰鍦拌兘鍔涖€備负姝?`xuanwu-server` 蹇呴』鎻愪緵杩愯鏃?API銆?

缁熶竴鍓嶇紑锛?

- `/runtime/v1`

### 9.1 浼氳瘽涓婁笅鏂囨煡璇?

`GET /runtime/v1/sessions/{runtime_session_id}/context`

鐢ㄩ€旓細

- 鏌ヨ褰撳墠璁惧杩炴帴涓庤兘鍔涚姸鎬?
- 渚?`AtlasClaw` Tool / Provider 鍋氬喅绛栧墠璇诲彇

鍝嶅簲绀轰緥锛?

```json
{
  "runtime_session_id": "rt-123",
  "device_id": "esp32-001",
  "client_id": "client-001",
  "atlas_session_key": "agent:main:user:device-esp32-001:xuanwu:dm:esp32-001",
  "connected": true,
  "capabilities": {
    "speaker": true,
    "camera": true,
    "mcp": true,
    "iot": true
  },
  "state": {
    "is_speaking": false,
    "listen_mode": "auto",
    "bind_status": "bound"
  }
}
```

### 9.2 鏈湴宸ュ叿鎵ц

`POST /runtime/v1/sessions/{runtime_session_id}/tool-executions`

鐢ㄩ€旓細

- `AtlasClaw` 璋冪敤璁惧鏈湴鑳藉姏

璇锋眰绀轰緥锛?

```json
{
  "name": "self_camera_take_photo",
  "arguments": {
    "question": "鎻忚堪褰撳墠鐪嬪埌鐨勫唴瀹?
  },
  "request_id": "toolreq-001"
}
```

鍝嶅簲绀轰緥锛?

```json
{
  "status": "ok",
  "request_id": "toolreq-001",
  "result": {
    "text": "鎽勫儚澶寸湅鍒版闈笂鏈変竴涓櫧鑹叉澂瀛愬拰涓€鏈功",
    "data": {}
  }
}
```

### 9.3 杩愯鏃舵墦鏂?

`POST /runtime/v1/sessions/{runtime_session_id}/interrupt`

鐢ㄩ€旓細

- `AtlasClaw` 涓诲姩瑕佹眰鏈湴鍋滄褰撳墠鎾姤鎴栦换鍔?

璇锋眰绀轰緥锛?

```json
{
  "reason": "new_user_turn"
}
```

鍝嶅簲绀轰緥锛?

```json
{
  "status": "ok",
  "interrupted": true
}
```

### 9.4 杩愯鏃惰璇濆姩浣?

`POST /runtime/v1/sessions/{runtime_session_id}/speak`

鐢ㄩ€旓細

- `AtlasClaw` 宸ュ叿閾鹃渶瑕佽澶囧嵆鏃舵挱鎶ユ椂浣跨敤
- 涓嶇粡杩囦富瀵硅瘽鍥炲閫氶亾

璇锋眰绀轰緥锛?

```json
{
  "text": "姝ｅ湪涓轰綘鎷嶇収锛岃绋嶇瓑",
  "interrupt_current": false
}
```

### 9.5 杩愯鏃惰璇?

鎵€鏈?`/runtime/v1/*` 鎺ュ彛缁熶竴閲囩敤鏈嶅姟鍒版湇鍔″瘑閽ワ細

- Header: `X-Xuanwu-Runtime-Secret`

榛樿绛栫暐锛?

- 瀵嗛挜浠?`xuanwu-server` 鏈湴閰嶇疆璇诲彇
- `AtlasClaw` 浣跨敤鐜鍙橀噺閰嶇疆
- 浠呭厑璁稿唴缃戣皟鐢?

## 10. AtlasClaw Provider 璁捐

### 10.1 鏂板 `xuanwu-runtime provider`

璇?provider 鐨勮亴璐ｆ槸灏?`AtlasClaw` 鍐呴儴 Tool 璋冪敤妗ユ帴鍒?`xuanwu-server` 鐨勮繍琛屾椂 API銆?

寤鸿鑳藉姏鍖呮嫭锛?

- `get_device_runtime_context`
- `speak_text`
- `interrupt_current_audio`
- `execute_device_tool`
- `get_device_capabilities`

寤鸿鐩綍锛?

- `C:/Projects/cmps/atlasclaw-providers/providers/xuanwu-runtime-provider`

濡傛殏涓嶄娇鐢ㄧ嫭绔?provider 浠撳簱锛屼篃鍙互鍏堟斁鍦ㄥ唴缃?provider 鎴?skills 鐩綍涓€?

### 10.2 Tool 娓呭崟

寤鸿绗竴鎵瑰伐鍏凤細

- `xuanwu_get_runtime_context`
- `xuanwu_take_photo`
- `xuanwu_speak_text`
- `xuanwu_interrupt`
- `xuanwu_execute_iot_action`
- `xuanwu_execute_mcp_tool`

### 10.3 Tool 杈撳叆绾﹀畾

鎵€鏈夊伐鍏烽兘蹇呴』鏀寔浠?`deps.extra.context` 涓鍙栵細

- `runtime_session_id`
- `device_id`
- `client_id`
- `capabilities`

鍘熷垯锛?

- 涓嶈姹傛瘡娆″伐鍏疯皟鐢ㄩ兘閲嶅浼?`runtime_session_id`
- 鑻ユ樉寮忎紶鍙備笌涓婁笅鏂囧啿绐侊紝浠ユ樉寮忎紶鍙備负鍑?

## 11. xuanwu-server 鍐呴儴閲嶆瀯璁捐

### 11.1 鏂板 `DialogueEngine`

寤鸿鏂板鎶借薄锛?

```python
class DialogueEngine(Protocol):
    async def run_turn(self, conn, user_text: str) -> None: ...
    async def abort_turn(self, conn) -> None: ...
```

瀹炵幇锛?

- `AtlasClawDialogueEngine`
- `LocalFallbackDialogueEngine`

寤鸿浣嶇疆锛?

- `main/xuanwu-server/core/providers/agent/dialogue_engine.py`
- `main/xuanwu-server/core/providers/agent/atlasclaw.py`
- `main/xuanwu-server/core/providers/agent/local_fallback.py`

### 11.2 `receiveAudioHandle.startToChat()` 璋冩暣

褰撳墠鑱岃矗锛?

- 瑙ｆ瀽鏂囨湰
- 鏈湴鎰忓浘璇嗗埆
- 鏈湴鑱婂ぉ

璋冩暣鍚庤亴璐ｏ細

- 鍋氳澶囩姸鎬佹鏌?
- `send_stt_message()`
- 璋冪敤 `conn.dialogue_engine.run_turn(conn, actual_text)`

涓嶅啀鐩存帴璋冪敤锛?

- `handle_user_intent()`
- `conn.chat()`

### 11.3 `intentHandler.py` 璋冩暣

鏈湴 `intentHandler.py` 涓嶅啀鏄富璺緞锛屼粎淇濈暀锛?

- 鍞ら啋璇嶅懡涓?
- 閫€鍑哄懡浠?
- 鏈湴璁惧绾х揣鎬ュ姩浣?

涓嶅啀璐熻矗锛?

- 涓绘剰鍥捐瘑鍒?
- 涓诲伐鍏疯鍒?
- 涓诲洖澶嶇敓鎴?

### 11.4 `connection.py` 璋冩暣

鏂板瀛楁锛?

- `runtime_session_id`
- `atlas_session_key`
- `dialogue_engine`
- `atlas_run_id`
- `atlas_stream_task`

绉婚櫎涓昏亴璐ｏ細

- 鏈湴涓诲璇濈敓鎴?
- 鏈湴涓诲伐鍏风紪鎺?
- 鏈湴涓昏蹇嗛┍鍔?

淇濈暀鑱岃矗锛?

- 杩炴帴鐢熷懡鍛ㄦ湡绠＄悊
- 闊抽娴佹帶
- 鏈湴璁惧鐘舵€?
- 鏈湴宸ュ叿鎵ц鍏ュ彛

### 11.5 `modules_initialize.py` 璋冩暣

鏂板 `Agent` 閰嶇疆鍧楋紝渚嬪锛?

```yaml
Agent:
  AtlasClaw:
    type: atlasclaw
    base_url: http://127.0.0.1:8000
    timeout_seconds: 120
    runtime_secret: ${XUANWU_RUNTIME_SECRET}
selected_module:
  Agent: AtlasClaw
```

鏂扮殑鍒濆鍖栭『搴忥細

- 蹇呴€夛細`ASR`
- 蹇呴€夛細`TTS`
- 蹇呴€夛細`Agent`
- 鍙€?fallback锛歚LLM` / `Intent` / `Memory`

### 11.6 `UnifiedToolHandler` 鐨勮鑹插彉鍖?

褰撳墠 `UnifiedToolHandler` 鏃㈡槸鏈湴宸ュ叿娉ㄥ唽鍣紝涔熸槸鏈湴涓婚摼璺伐鍏锋墽琛屽櫒銆?

閲嶆瀯鍚庡彉涓猴細

- 璁惧鏈湴鑳藉姏鎵ц鍣?
- `AtlasClaw` 杩愯鏃?API 鑳屽悗鐨勬墽琛屾牳蹇?

鍗筹細

- 涓嶅啀涓昏鏈嶅姟鏈湴 `LLM function calling`
- 杞€屾湇鍔?`AtlasClaw -> runtime API -> UnifiedToolHandler`

## 12. AtlasClaw 鍐呴儴鏀归€犺璁?

### 12.1 `AgentRunRequest` 鎵╁睍

淇敼浣嶇疆锛?

- `C:/Projects/cmps/atlasclaw/app/atlasclaw/api/schemas.py`

鏂板瀛楁锛?

```python
class AgentRunRequest(BaseModel):
    session_key: str
    message: str
    model: Optional[str] = None
    timeout_seconds: int = 600
    context: dict[str, Any] = Field(default_factory=dict)
```

### 12.2 `routes_agent.py` 璋冩暣

鐩爣锛?

- 鎺ュ彈 `context`
- 浼犲叆 `execute_agent_run(...)`

### 12.3 `run_service.py` 璋冩暣

灏?`request.context` 娉ㄥ叆锛?

- `build_scoped_deps(..., extra={"context": request.context, "agent_id": target_agent_id})`

杩欐牱鎵€鏈?Skills / Tools 鍙互浠庯細

- `ctx.deps.extra["context"]`

璇诲彇璁惧涓婁笅鏂囥€?

### 12.4 Skill / Tool 浣跨敤绾﹀畾

鎵€鏈変笌璁惧鐩稿叧鐨?AtlasClaw Tool 蹇呴』閬靛惊锛?

- 璇诲彇 `runtime_session_id`
- 涓嶇洿鎺ユ寔鏈?WebSocket
- 涓嶇洿鎺ヤ緷璧?`xuanwu-server` 鍐呴儴浠ｇ爜
- 鍙€氳繃杩愯鏃?API 璋冪敤璁惧鏈湴鑳藉姏

## 13. 澶辫触澶勭悊涓庨檷绾х瓥鐣?

### 13.1 AtlasClaw 涓嶅彲杈?

榛樿绛栫暐锛?

- 棣栭€夐噸璇曚竴娆?
- 澶辫触鍚庤繘鍏ユ湰鍦?fallback 寮曟搸

fallback 鑼冨洿锛?

- 绠€鍗曢棽鑱?
- 鍥哄畾妯℃澘鍥炲
- 鍩虹鏈湴宸ュ叿

涓嶄繚璇侊細

- 澶氭浠ｇ悊浠诲姟
- 闀跨▼璁板繂涓€鑷存€?

### 13.2 杩愯鏃跺伐鍏疯皟鐢ㄥけ璐?

鑻?`AtlasClaw` 璋冪敤 `xuanwu runtime API` 澶辫触锛?

- 杩斿洖缁撴瀯鍖栭敊璇粰 `AtlasClaw`
- 鐢?`AtlasClaw` 鍐冲畾鏄惁鏀圭敤鍏朵粬宸ュ叿鎴栧悜鐢ㄦ埛瑙ｉ噴澶辫触

### 13.3 璁惧鏂嚎

鑻ヨ澶囨柇绾匡細

- 鏈湴 `runtime_session_registry` 绔嬪埢澶辨晥璇?`runtime_session_id`
- `runtime API` 杩斿洖 `410 Gone` 鎴?`404 Not Found`
- `AtlasClaw` 鏀跺埌鍚庡仠姝㈣绫昏澶囧姩浣?

### 13.4 鎵撴柇绛栫暐

褰撶敤鎴锋柊涓€杞闊宠緭鍏ュ紑濮嬫椂锛?

- `xuanwu-server` 浼樺厛鏈湴涓柇 TTS 鎾姤
- 濡傚瓨鍦ㄥ湪閫?`AtlasClaw run_id`锛岃皟鐢?`/agent/runs/{run_id}/abort`

## 14. 瀹夊叏璁捐

### 14.1 鏈嶅姟闂磋璇?

- `AtlasClaw -> xuanwu-server runtime API` 蹇呴』浣跨敤鏈嶅姟瀵嗛挜
- 瀵嗛挜涓嶈兘澶嶇敤璁惧 JWT
- 鎵€鏈夎皟鐢ㄨ褰曡姹?ID 鍜?session ID

### 14.2 宸ュ叿鏉冮檺杈圭晫

鍘熷垯锛?

- `AtlasClaw` 璐熻矗鍐崇瓥
- `xuanwu-server` 璐熻矗鎵ц
- 鐪熸鎺ヨЕ璁惧纭欢銆佹憚鍍忓ご銆両oT銆侀害鍏嬮鐨勬潈闄愯竟鐣岄兘鐣欏湪鏈湴

### 14.3 瀹¤

闇€瑕佽褰曪細

- 姣忔 `/agent/run` 璇锋眰
- 姣忔杩愯鏃跺伐鍏锋墽琛?
- 姣忔涓柇涓庡け璐?
- 姣忔 fallback 瑙﹀彂

## 15. 鍒嗛樁娈靛疄鏂借鍒?

### Phase 1: 鎺ュ彛鍐荤粨

- 鍐荤粨 `session_key` 瑙勮寖
- 鍐荤粨 `AgentRunRequest.context`
- 鍐荤粨 runtime API 濂戠害
- 鍐荤粨 `xuanwu-runtime` tool 娓呭崟

### Phase 2: AtlasClaw 瀵规帴灞?

- 澧炲姞 `AtlasClawDialogueEngine`
- 鎵撻€?`/agent/run` 涓?SSE stream
- 鎵撻€氭湰鍦版枃鏈埌 TTS 鐨勬ˉ鎺?

### Phase 3: 杩愯鏃跺伐鍏锋ˉ

- 澧炲姞 `runtime/v1` API
- 灏?`UnifiedToolHandler` 鏀惧埌杩愯鏃?API 鑳屽悗
- 澧炲姞 `xuanwu-runtime provider`

### Phase 4: 涓婚摼璺垏鎹?

- `startToChat()` 鏀逛负璧?`DialogueEngine`
- 鏈湴 `Intent/LLM/Memory` 浠庝富閾捐矾绉婚櫎
- 鍔犲叆 fallback

### Phase 5: 娓呯悊涓庝笅绾?

- 鍋滄渚濊禆鏈湴涓绘剰鍥句笌鏈湴涓昏亰澶╅€昏緫
- 娓呯悊閰嶇疆涓粯璁ょ殑鏈湴 `LLM/Intent/Memory` 涓昏矾寰?
- 璇勪及骞朵笅绾块潪鏍稿績妯″潡

## 16. 楠屾敹鏍囧噯

瀹屾垚鍚庡繀椤绘弧瓒充互涓嬫爣鍑嗭細

- 璁惧绔枃鏈緭鍏ラ粯璁ゅ叏閮ㄨ繘鍏?`AtlasClaw`
- 鏈湴涓嶅啀鎵挎媴涓诲洖澶嶇敓鎴?
- `AtlasClaw` 鑳介€氳繃 SSE 鎸佺画杩斿洖鏂囨湰娴?
- `xuanwu-server` 鑳芥妸 `assistant` 浜嬩欢绋冲畾杞崲涓?TTS 鎾姤
- `AtlasClaw` 鑳介€氳繃 runtime API 璋冪敤璁惧鏈湴宸ュ叿
- 鐢ㄦ埛鎵撴柇鏃惰兘鍚屾椂涓柇鏈湴 TTS 鍜岃繙绔?`AtlasClaw run`
- `AtlasClaw` 涓嶅彲鐢ㄦ椂绯荤粺鑳借繘鍏ユ槑纭殑 fallback 妯″紡
- 褰撳墠璁惧鍗忚 `hello` / `ping` / `abort` / `listen` / OTA 涓嶅彈褰卞搷

## 17. 浠ｇ爜鏀瑰姩娓呭崟

### 17.1 xuanwu-server

閲嶇偣淇敼锛?

- `main/xuanwu-server/core/handle/receiveAudioHandle.py`
- `main/xuanwu-server/core/handle/intentHandler.py`
- `main/xuanwu-server/core/connection.py`
- `main/xuanwu-server/core/utils/modules_initialize.py`
- `main/xuanwu-server/core/providers/tools/unified_tool_handler.py`

寤鸿鏂板锛?

- `main/xuanwu-server/core/providers/agent/dialogue_engine.py`
- `main/xuanwu-server/core/providers/agent/atlasclaw.py`
- `main/xuanwu-server/core/providers/agent/atlasclaw_stream_bridge.py`
- `main/xuanwu-server/core/providers/agent/local_fallback.py`
- `main/xuanwu-server/core/runtime/session_registry.py`
- `main/xuanwu-server/core/api/runtime_tool_handler.py`

### 17.2 AtlasClaw

閲嶇偣淇敼锛?

- `C:/Projects/cmps/atlasclaw/app/atlasclaw/api/schemas.py`
- `C:/Projects/cmps/atlasclaw/app/atlasclaw/api/routes_agent.py`
- `C:/Projects/cmps/atlasclaw/app/atlasclaw/api/services/run_service.py`

寤鸿鏂板锛?

- `xuanwu-runtime provider`
- `xuanwu-runtime tools`

## 18. 榛樿瀹炵幇鍋囪

涓洪伩鍏嶅疄鐜版湡鍐嶅仛浜у搧鍐崇瓥锛岄粯璁ら噰鐢ㄤ互涓嬪亣璁撅細

- `AtlasClaw` 涓哄敮涓€涓诲璇濆紩鎿?
- 璁惧鏈湴瀵硅瘽寮曟搸鍙綔涓?fallback
- `session_key` 鐢?`xuanwu-server` 鏋勯€?
- `AtlasClaw` 缁х画淇濈暀鍏剁幇鏈?SSE 璇箟锛屼笉鍋氬崗璁噸鍐?
- 璁惧鏈湴鑳藉姏閫氳繃 HTTP runtime API 鏆撮湶锛屼笉鍋氳繘绋嬪唴鐩磋繛
- `UnifiedToolHandler` 淇濈暀锛屽苟杞瀷涓烘湰鍦版墽琛屽眰
- 鎵€鏈夎澶囨湰鍦伴珮鏉冮檺鍔ㄤ綔蹇呴』鐢?`xuanwu-server` 鎵ц



