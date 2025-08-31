import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from js import document, console
from pyodide.ffi import create_proxy

# 创建模拟数据
def load_simulated_data():
    """创建模拟的体节运动数据"""
    np.random.seed(42)
    time = np.linspace(0, 10, 500)
    
    segments = ["V_", "D_", "VL", "DL"]
    subpoints = ["Subpoint A", "Subpoint B", "Subpoint C", "Subpoint D"]
    
    data = {}
    for segment in segments:
        data[segment] = {}
        for subpoint in subpoints:
            # 生成更真实的位置和速度数据
            freq = np.random.uniform(0.5, 2.0)
            phase = np.random.uniform(0, 2*np.pi)
            
            pos_x = 2 * np.sin(2 * np.pi * freq * time + phase) + np.random.normal(0, 0.2, len(time))
            pos_y = 1.5 * np.sin(2 * np.pi * freq * time + phase + np.pi/3) + np.random.normal(0, 0.2, len(time))
            pos_z = np.sin(2 * np.pi * freq * time + phase + np.pi/2) + np.random.normal(0, 0.2, len(time))
            
            # 计算速度（位置的一阶导数）
            dt = time[1] - time[0]
            vel_x = np.gradient(pos_x, dt)
            vel_y = np.gradient(pos_y, dt)
            vel_z = np.gradient(pos_z, dt)
            
            data[segment][subpoint] = pd.DataFrame({
                'time': time,
                'pos_x': pos_x,
                'pos_y': pos_y,
                'pos_z': pos_z,
                'vel_x': vel_x,
                'vel_y': vel_y,
                'vel_z': vel_z
            })
    
    return segments, subpoints, data

# 初始化数据
segments, subpoints, data = load_simulated_data()

# 绘制图表
def plot_data(segment, subpoint, axis):
    """绘制选定的数据"""
    if segment in data and subpoint in data[segment]:
        df = data[segment][subpoint]
        time = df['time']
        position = df[f'pos_{axis}']
        velocity = df[f'vel_{axis}']

        # 创建位置图表
        fig1, ax1 = plt.subplots(figsize=(8, 3))
        ax1.plot(time, position, label=f'{axis.upper()} Position', color='#1f77b4', linewidth=2)
        ax1.set_ylabel('Position (mm)')
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend(loc='upper right')
        ax1.set_title('Position Curve')
        
        # 创建速度图表
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        ax2.plot(time, velocity, label=f'{axis.upper()} Velocity', color='#ff7f0e', linewidth=2)
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Velocity (mm/s)')
        ax2.grid(True, linestyle='--', alpha=0.7)
        ax2.legend(loc='upper right')
        ax2.set_title('Velocity Curve')
        ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        
        return fig1, fig2
    else:
        return None, None

# 更新图表函数
def update_charts(*args):
    """更新显示的图表"""
    # 获取用户选择
    segment = document.getElementById("segmentSelect").value
    subpoint = document.getElementById("subpointSelect").value
    
    # 获取选中的坐标轴
    axis_buttons = document.getElementsByName("axis")
    axis = "x"
    for btn in axis_buttons:
        if btn.checked:
            axis = btn.id.replace("Axis", "").lower()
            break
    
    # 绘制新图表
    fig1, fig2 = plot_data(segment, subpoint, axis)
    
    # 清除旧图表
    position_chart = document.getElementById("positionChart")
    velocity_chart = document.getElementById("velocityChart")
    position_chart.innerHTML = ""
    velocity_chart.innerHTML = ""
    
    # 显示新图表
    if fig1 and fig2:
        # 将图表转换为HTML
        from io import BytesIO
        import base64
        
        # 位置图表
        buf1 = BytesIO()
        fig1.savefig(buf1, format="png", bbox_inches="tight")
        buf1.seek(0)
        img_str1 = base64.b64encode(buf1.read()).decode("utf-8")
        position_chart.innerHTML = f'<img src="data:image/png;base64,{img_str1}" class="w-100">'
        
        # 速度图表
        buf2 = BytesIO()
        fig2.savefig(buf2, format="png", bbox_inches="tight")
        buf2.seek(0)
        img_str2 = base64.b64encode(buf2.read()).decode("utf-8")
        velocity_chart.innerHTML = f'<img src="data:image/png;base64,{img_str2}" class="w-100">'
        
        plt.close(fig1)
        plt.close(fig2)

# 创建代理函数以便从JavaScript调用
updateCharts = create_proxy(update_charts)

# 初始绘制
update_charts()
