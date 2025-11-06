#!/usr/bin/env python3
"""
Rich 可视化模块

职责：
1. 从队列读取数据
2. 实时更新3个区域的显示
3. 一个窗口分3个区域（不是3个独立窗口）
"""

import queue
import time
from datetime import datetime
from typing import Dict, Any
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.console import Group


class Display:
    """可视化显示器"""

    MISSION_NAMES = {
        1: "原地起飞5米",
        2: "无人机原地降落",
        3: "返航",
        4: "前往指定点",
        5: "预设多航点任务1",
        6: "预设多航点任务2",
        7: "预设多航点任务3"
    }

    def __init__(self, data_queue: queue.Queue):
        """
        Args:
            data_queue: 数据队列
        """
        self.queue = data_queue

        # 状态存储
        self.drone_states = {
            1: {'position': None, 'targets': None, 'task': None, 'error': None, 'pos_count': 0, 'tar_count': 0, 'token': None, 'account': None},
            2: {'position': None, 'targets': None, 'task': None, 'error': None, 'pos_count': 0, 'tar_count': 0, 'token': None, 'account': None},
            3: {'position': None, 'targets': None, 'task': None, 'error': None, 'pos_count': 0, 'tar_count': 0, 'token': None, 'account': None}
        }

    def run(self):
        """启动可视化循环"""
        with Live(self._render(), auto_refresh=False, screen=True) as live:
            while True:
                # 非阻塞读取所有队列数据
                updated = False
                try:
                    while True:
                        msg_type, drone_id, data = self.queue.get_nowait()
                        self._update_state(msg_type, drone_id, data)
                        updated = True
                except queue.Empty:
                    pass

                # 更新显示
                if updated:
                    live.update(self._render(), refresh=True)

                time.sleep(0.05)  # 20Hz 刷新

    def _update_state(self, msg_type: str, drone_id: int, data: Any):
        """更新状态"""
        state = self.drone_states[drone_id]

        if msg_type == 'position':
            state['position'] = data
            state['pos_count'] += 1
            # 保存token和account
            if data.get('_token'):
                state['token'] = data.get('_token')
                state['account'] = data.get('_account')
        elif msg_type == 'targets':
            state['targets'] = data
            state['tar_count'] += 1
        elif msg_type == 'task':
            state['task'] = data
        elif msg_type == 'error':
            state['error'] = (datetime.now(), data)

    def _render(self) -> Layout:
        """渲染整个布局"""
        layout = Layout()

        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body"),
        )

        layout["header"].update(Panel(
            "[bold cyan]IVAS 真实客户端 - 实时监控[/bold cyan]",
            style="bold white on blue"
        ))

        # Body 分成3个区域
        layout["body"].split_column(
            Layout(name="positions", ratio=2),
            Layout(name="targets", ratio=2),
            Layout(name="tasks", ratio=1)
        )

        layout["positions"].update(self._make_position_panel())
        layout["targets"].update(self._make_targets_panel())
        layout["tasks"].update(self._make_tasks_panel())

        return layout

    def _make_position_panel(self) -> Panel:
        """创建位置数据面板"""
        table = Table(title="位置数据上报 (10Hz)", show_header=True, header_style="bold magenta")

        table.add_column("无人机", style="cyan", width=8)
        table.add_column("账号", style="magenta", width=10)
        table.add_column("Token", style="dim white", width=8)
        table.add_column("纬度(userX)", style="green", width=12)
        table.add_column("经度(userY)", style="green", width=12)
        table.add_column("高度(userZ)", style="yellow", width=10)
        table.add_column("方向角", style="blue", width=8)
        table.add_column("动/静", style="white", width=6)
        table.add_column("上报次数", style="white", width=10)

        for drone_id in [1, 2, 3]:
            state = self.drone_states[drone_id]
            pos = state['position']
            token = state['token']
            account = state['account']

            if pos:
                motion_text = "移动" if pos.get('motion') == 1 else "静止"
                token_prefix = token[-5:] if token else "N/A"
                account_text = account if account else "N/A"

                table.add_row(
                    f"DRONE-{drone_id}",
                    account_text,
                    f"[dim]{token_prefix}...[/dim]",
                    f"{pos.get('userX', 0):.6f}",
                    f"{pos.get('userY', 0):.6f}",
                    f"{pos.get('userZ', 0):.2f}m",
                    f"{pos.get('azimuth', 0)}°",
                    motion_text,
                    f"{state['pos_count']}"
                )
            else:
                table.add_row(
                    f"DRONE-{drone_id}",
                    "[dim]等待...[/dim]",
                    "[dim]N/A[/dim]",
                    "[dim]等待数据...[/dim]",
                    "",
                    "",
                    "",
                    "",
                    "0",
                )

        return Panel(table, border_style="green")

    def _make_targets_panel(self) -> Panel:
        """创建目标数据面板"""
        table = Table(title="目标数据上报 (10Hz)", show_header=True, header_style="bold magenta")

        table.add_column("无人机", style="cyan", width=8)
        table.add_column("目标数", style="green", width=8)
        table.add_column("最新目标", style="yellow", width=60)
        table.add_column("上报次数", style="white", width=10)

        for drone_id in [1, 2, 3]:
            state = self.drone_states[drone_id]
            tar = state['targets']

            if tar:
                obj_cnt = tar.get('obj_cnt', 0)
                objs = tar.get('objs', [])

                if objs:
                    # 显示第一个目标的信息
                    first_obj = objs[0]
                    cls = first_obj.get('cls', 0)
                    cls_name = {0: "人", 1: "车", 2: "飞机"}.get(cls, "未知")
                    gis = first_obj.get('gis', [0, 0, 0])
                    obj_info = f"{cls_name} @ ({gis[0]:.6f}, {gis[1]:.6f}, {gis[2]:.2f}m)"
                else:
                    obj_info = "[dim]无目标[/dim]"

                table.add_row(
                    f"DRONE-{drone_id}",
                    f"{obj_cnt}",
                    obj_info,
                    f"{state['tar_count']}"
                )
            else:
                table.add_row(
                    f"DRONE-{drone_id}",
                    "[dim]等待数据...[/dim]",
                    "",
                    "0"
                )

        return Panel(table, border_style="yellow")

    def _make_tasks_panel(self) -> Panel:
        """创建任务数据面板"""
        table = Table(title="任务轮询 (0.2Hz / 5秒)", show_header=True, header_style="bold magenta")

        table.add_column("无人机", style="cyan", width=8)
        table.add_column("任务类型", style="green", width=20)
        table.add_column("任务详情", style="yellow", width=50)
        table.add_column("状态", style="white", width=10)

        for drone_id in [1, 2, 3]:
            state = self.drone_states[drone_id]
            task = state['task']

            if task and task.get('code') == 200 and task.get('data'):
                data = task.get('data')
                mission = data.get('mission')
                mission_name = self.MISSION_NAMES.get(mission, f"未知任务({mission})")

                # 构建详情
                details = []
                if mission == 4:
                    lat = data.get('lat', 0)
                    lon = data.get('lon', 0)
                    alt = data.get('alt', 0)
                    details.append(f"目标: ({lon:.6f}, {lat:.6f}, {alt:.2f}m)")

                target_id = data.get('id')
                if target_id:
                    if target_id == 99:
                        details.append("目标: 所有无人机")
                    else:
                        details.append(f"目标: DRONE-{target_id}")

                details_text = " | ".join(details) if details else ""

                table.add_row(
                    f"DRONE-{drone_id}",
                    mission_name,
                    details_text,
                    "[green]接收[/green]"
                )
            else:
                error = state.get('error')
                if error:
                    timestamp, err_msg = error
                    age = (datetime.now() - timestamp).total_seconds()
                    if age < 5:  # 5秒内的错误
                        table.add_row(
                            f"DRONE-{drone_id}",
                            "[red]错误[/red]",
                            f"{err_msg}",
                            "[red]异常[/red]"
                        )
                        continue

                table.add_row(
                    f"DRONE-{drone_id}",
                    "[dim]等待任务...[/dim]",
                    "",
                    "[dim]空闲[/dim]"
                )

        return Panel(table, border_style="blue")
