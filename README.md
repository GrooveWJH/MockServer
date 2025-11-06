# MockServer

## IVAS Python SDK

IVAS 无人机客户端 SDK，提供与 IVAS 服务器交互的完整接口。

### 功能特性

- **位置数据上报**: 自动生成并上报无人机位置数据
- **目标检测上报**: 上报目标检测数据（人、车、飞机等）
- **任务轮询**: 定期从服务器获取任务指令
- **Token 管理**: 自动处理登录和 token 过期重新登录
- **可配置频率**: 灵活配置上报频率和轮询频率
- **多设备支持**: 可同时运行多个客户端实例

### 安装方法

#### 方法 1: 从源码安装（推荐）

```bash
# 在项目根目录下执行
cd /Users/groovewjh/Project/work/SYSU/MockServer
pip install -e .
```

使用 `-e` 参数安装为可编辑模式，方便开发调试。

#### 方法 2: 直接安装

```bash
cd /Users/groovewjh/Project/work/SYSU/MockServer
pip install .
```

### 快速开始

#### 基本使用

```python
from ivas import IVASClient

# 创建客户端实例
client = IVASClient(
    device_code=1,              # 设备编号
    account='ZSDX001',          # 登录账号
    password='your_password',   # 登录密码
    base_lat=23.0,              # 基准纬度
    base_lon=113.0,             # 基准经度
    base_alt=100.0,             # 基准海拔
    coord_range={               # 坐标随机范围
        'lat_offset': 0.001,
        'lon_offset': 0.001,
        'alt_offset': 10.0
    },
    base_url='http://localhost:5001',  # IVAS 服务器地址
    report_hz=1.0,              # 位置上报频率 (Hz)
    task_hz=0.2                 # 任务轮询频率 (Hz)
)

# 运行客户端
client.run()
```

#### 运行示例程序

```bash
# 单设备示例
python example.py

# 或者在其他目录运行（安装包后）
cd /path/to/your/project
python example.py
```

#### 多设备示例

```python
import threading
from ivas import IVASClient

# 配置多个设备
devices = [
    {'device_code': 1, 'account': 'ZSDX001', 'password': 'pwd1', 'base_lat': 23.0, 'base_lon': 113.0},
    {'device_code': 2, 'account': 'ZSDX002', 'password': 'pwd2', 'base_lat': 23.001, 'base_lon': 113.001},
    {'device_code': 3, 'account': 'ZSDX003', 'password': 'pwd3', 'base_lat': 23.002, 'base_lon': 113.002}
]

clients = []
threads = []

for device in devices:
    # 补充配置
    device.update({
        'base_alt': 100.0,
        'coord_range': {'lat_offset': 0.001, 'lon_offset': 0.001, 'alt_offset': 10.0},
        'base_url': 'http://localhost:5001',
        'report_hz': 1.0,
        'task_hz': 0.2
    })

    client = IVASClient(**device)
    clients.append(client)

    thread = threading.Thread(target=client.run, daemon=True)
    thread.start()
    threads.append(thread)

# 等待运行...
```

### API 文档

#### IVASClient 类

**初始化参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `device_code` | int | 设备编号 (例如: 1, 2, 3) |
| `account` | str | 登录账号 (例如: ZSDX001) |
| `password` | str | 登录密码 |
| `base_lat` | float | 基准纬度 |
| `base_lon` | float | 基准经度 |
| `base_alt` | float | 基准海拔高度 |
| `coord_range` | dict | 坐标随机范围，包含 `lat_offset`, `lon_offset`, `alt_offset` |
| `base_url` | str | IVAS 服务器地址 |
| `display_queue` | Queue | 可视化队列（可选） |
| `report_hz` | float | 位置和目标上报频率，单位 Hz（默认 1.0） |
| `task_hz` | float | 任务轮询频率，单位 Hz（默认 0.2） |

**主要方法:**

- `run()`: 启动客户端主循环（阻塞）
- `stop()`: 停止客户端运行
- `login()`: 手动执行登录（通常自动调用）

### 项目结构

```
MockServer/
├── ivas/                   # IVAS SDK 包
│   ├── __init__.py        # 包初始化文件
│   └── client.py          # 客户端核心实现
├── Real/                   # 原始实现（保留）
│   ├── drone.py           # 原始 Drone 类
│   ├── display.py         # 可视化模块
│   ├── main.py            # 原始主程序
│   └── config.json        # 配置文件
├── setup.py               # 包安装配置
├── example.py             # 使用示例
├── requirements.txt       # 依赖列表
└── README.md              # 本文件
```

### 依赖项

- Python >= 3.7
- requests >= 2.25.0

### 注意事项

1. 确保 IVAS 服务器已启动并可访问
2. 配置正确的账号、密码和服务器地址
3. 根据实际需求调整上报频率和轮询频率
4. 多设备运行时注意服务器性能

### 开发模式

如果需要修改 SDK 代码，使用可编辑模式安装：

```bash
pip install -e .
```

这样修改代码后无需重新安装即可生效。

### 许可证

MIT License

### 技术支持

如有问题，请联系 IVAS 开发团队。
