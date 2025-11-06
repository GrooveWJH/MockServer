# IVAS 真实客户端

连接真实 IVAS 服务器的无人机客户端。

## 文件结构

```
Real/
├── config.json     # 配置文件
├── main.py         # 入口程序
├── drone.py        # 无人机核心逻辑
└── display.py      # Rich 可视化
```

## 快速开始

### 1. 安装依赖

```bash
pip3 install requests rich
```

### 2. 配置服务器

编辑 `config.json`：

```json
{
  "server": {
    "base_url": "http://真实服务器IP:端口",
    "account": "ZSDX001",
    "password": "000000"
  },
  "drones": [
    {"device_code": 1, "base_lat": 23.0, "base_lon": 113.0, "base_alt": 100.0},
    {"device_code": 2, "base_lat": 23.1, "base_lon": 113.1, "base_alt": 120.0},
    {"device_code": 3, "base_lat": 23.2, "base_lon": 113.2, "base_alt": 150.0}
  ],
  "coord_range": {
    "lat_offset": 0.01,
    "lon_offset": 0.01,
    "alt_offset": 20.0
  },
  "intervals": {
    "report_hz": 10,
    "task_hz": 0.2
  }
}
```

### 3. 运行

```bash
cd Real
python3 main.py
```

## 功能特性

✅ **3个无人机同时运行**
- deviceCode: 1, 2, 3
- 独立线程，互不干扰

✅ **自动登录获取 token**
- 启动时自动登录
- token 过期自动重登录

✅ **数据上报 (10Hz)**
- 位置数据：`POST /reportUserData` (URL参数)
- 目标数据：`POST /postTarPos` (JSON body)

✅ **任务轮询 (0.2Hz / 5秒)**
- 任务指令：`GET /outdoorTask`
- 支持7种任务类型

✅ **Rich 实时可视化**
- 一个窗口，3个区域
- 实时显示位置、目标、任务数据
- 彩色表格，清晰易读

## 接口说明

### 1. 位置上报 (10Hz)

```
POST /jk-ivas/third/controller/reportUserData
传参方式: URL 参数 (params)
Header: token
```

### 2. 目标上报 (10Hz)

```
POST /jk-ivas/non/controller/postTarPos
传参方式: JSON body
Header: token
```

### 3. 任务轮询 (0.2Hz)

```
GET /jk-ivas/third/controller/outdoorTask
Header: token
```

## 数据格式

### 位置数据
```python
{
    'deviceCode': 1,
    'userX': 23.123456,      # 纬度
    'userY': 113.123456,     # 经度
    'userZ': 120.5,          # 海拔
    'azimuth': 180,          # 方向角
    'localTime': 1234567890, # 毫秒时间戳
    'motion': 1,             # 0=静止, 1=移动
    'validCount': 8,         # 卫星数
    'roomId': 22,
    'refPositionType': 0
}
```

### 目标数据
```python
{
    'timestamp': 1234567890,
    'obj_cnt': 2,
    'objs': [
        {
            'id': 1001,
            'cls': 0,              # 0=人, 1=车, 2=飞机
            'gis': [113.12, 23.45, 100.0],
            'bbox': [320, 240, 50, 80],
            'obj_img': 'http://...'
        }
    ]
}
```

### 任务数据
```python
{
    'code': 200,
    'msg': '获取任务成功',
    'data': {
        'mission': 4,      # 1-7
        'id': 1,           # 目标无人机ID (99=所有)
        'lat': 23.5,       # 任务4需要
        'lon': 113.5,
        'alt': 150.0
    }
}
```

## 任务类型

| Mission | 任务名称 | 说明 |
|---------|----------|------|
| 1 | 原地起飞5米 | 可指定所有无人机 |
| 2 | 原地降落 | 可指定所有无人机 |
| 3 | 返航 | 可指定所有无人机 |
| 4 | 前往指定点 | 需要经纬高参数 |
| 5 | 预设多航点任务1 | 预设任务 |
| 6 | 预设多航点任务2 | 预设任务 |
| 7 | 预设多航点任务3 | 预设任务 |

## 架构设计

基于 **Linus Torvalds 设计哲学**：

- ✅ **简洁**：3个文件，4个核心概念
- ✅ **高效**：单线程处理多频率，零锁竞争
- ✅ **可维护**：清晰的模块划分，易于理解
- ✅ **零过度设计**：没有抽象层，没有依赖注入

### 数据流

```
config.json → 登录 → token
           ↓
3个Drone线程 → HTTP请求 → Queue
           ↓
Display线程 → Rich Live 渲染
```

## 常见问题

**Q: 如何修改服务器地址？**
A: 编辑 `config.json` 中的 `server.base_url`

**Q: 如何修改上报频率？**
A: 编辑 `config.json` 中的 `intervals.report_hz` 和 `task_hz`

**Q: 如何修改坐标范围？**
A: 编辑 `config.json` 中的 `coord_range`

**Q: Token 过期怎么办？**
A: 自动处理，收到 401 错误会自动重新登录

**Q: 如何添加第4个无人机？**
A: 在 `config.json` 的 `drones` 数组中添加新配置

## 系统要求

- Python 3.7+
- requests
- rich

## 作者

基于 Linus-Torvalds 架构设计
