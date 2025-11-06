#!/usr/bin/env python3
"""
IVAS 真实客户端 - 主入口

使用方法：
    python main.py
"""

import json
import queue
import threading
import sys
from pathlib import Path

from drone import Drone
from display import Display


def load_config(config_file='config.json'):
    """加载配置文件"""
    config_path = Path(__file__).parent / config_file
    if not config_path.exists():
        print(f"错误: 配置文件 {config_file} 不存在")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    """主函数"""
    print("=" * 60)
    print("IVAS 真实客户端")
    print("=" * 60)
    print()

    # 1. 加载配置
    print("1. 加载配置文件...")
    config = load_config()
    print(f"   服务器: {config['server']['base_url']}")
    print(f"   无人机数量: {len(config['drones'])}")
    print()

    # 2. 创建队列
    print("2. 创建通信队列...")
    display_queue = queue.Queue(maxsize=1000)
    print(f"   队列容量: 1000")
    print()

    # 3. 启动无人机线程
    print("3. 启动无人机线程（每个无人机独立登录）...")
    threads = []

    for drone_cfg in config['drones']:
        drone = Drone(
            device_code=drone_cfg['device_code'],
            account=drone_cfg['account'],
            password=config['server']['password'],
            base_lat=drone_cfg['base_lat'],
            base_lon=drone_cfg['base_lon'],
            base_alt=drone_cfg['base_alt'],
            coord_range=config['coord_range'],
            base_url=config['server']['base_url'],
            display_queue=display_queue,
            report_hz=config['intervals']['report_hz'],
            task_hz=config['intervals']['task_hz']
        )

        t = threading.Thread(
            target=drone.run,
            name=f"Drone-{drone_cfg['device_code']}",
            daemon=True
        )
        t.start()
        threads.append(t)

        print(f"   ✓ DRONE-{drone_cfg['device_code']} ({drone_cfg['account']}) 已启动")

    print()
    print("4. 启动可视化...")
    print()
    print("=" * 60)
    print("系统运行中 (按 Ctrl+C 退出)")
    print("=" * 60)
    print()

    # 4. 启动可视化（主线程）
    try:
        display = Display(display_queue)
        display.run()
    except KeyboardInterrupt:
        print("\n\n收到退出信号，正在停止...")
        print("系统已停止")


if __name__ == '__main__':
    main()
