# -*- coding: utf-8 -*-
# @Author  : zx jiang
# @Time    : 2025-02-02 11:27
# @File    : demo.py
# @Software: Cursor

from DrissionPage import Chromium, ChromiumOptions
import urllib.parse
import os, sys
import shutil
import subprocess
from loguru import logger
import traci # noqa
import time


def download_osm_file(loc: str, source_path: str, destination_path: str):
    """
    从 OpenStreetMap 下载指定城市的 OSM 文件并移动到指定位置。
    
    :param city: 城市名称（如 '杭州市')
    :param source_path: 下载后的 OSM 文件路径
    :param destination_path: 文件移动后的目标路径
    """
    # 设置查询参数
    params = {
        'q': loc,
        'format': 'geocodejson',
        'addressdetails': '1',
        'accept-language': 'zh',
        'zoom': '17',
        'limit': '1',
    }

    # 构建 URL
    url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(params)

    # 配置 Chromium 浏览器为无头模式
    co = ChromiumOptions().headless()
    browser = Chromium(co)

    try:
        # 打开 OSM 查询页面
        tab = browser.new_tab(url)

        # 获取坐标信息
        coordinates = tab.json['features'][0]['geometry']['coordinates']
        coordStr = f"{coordinates[1]}/{coordinates[0]}"  # 纬度/经度

        logger.warning(f"coordStr: {coordStr}")

        # 构建 OSM 文件下载页面的 URL
        coordinates_url = f'https://www.openstreetmap.org/export#map=17/{coordStr}'
        newTab = browser.new_tab(coordinates_url)

        # 找到并点击 "导出" 按钮
        selector = 'x://*[@id="export_commit"]/div/input'
        export = newTab.ele(selector)
        export.click()

        # 等待下载完成
        newTab.wait(5)

        logger.success('OSM File Downloaded!')

        # 检查目标文件夹是否存在，不存在则创建
        if not os.path.exists(os.path.dirname(destination_path)):
            os.makedirs(os.path.dirname(destination_path))

        # 移动文件
        if os.path.exists(source_path):
            shutil.move(source_path, destination_path)
            logger.info(f"File successfully moved to {destination_path}")
        else:
            logger.error(f"File not found: {source_path}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    
    finally:
        browser.quit()

def convert_osm_to_net(osm_path: str, net_path: str):
    os.system(f'cmd /c "netconvert --osm {osm_path} -o {net_path}"')

def generate_random_trips(net_path: str, trips_path: str):
    random_trips_path = os.path.join(tools, 'randomTrips.py')
    command = f'python {random_trips_path} -n {net_path} -r {trips_path} -e 500 -l'
    subprocess.run(command, shell=True, check=True)  # 500 is the number of vehicles -l is the length of the trip 

def sim(sumocfgfile: str):
    sumoConfig = ["-c", sumocfgfile, "--time-to-teleport", "200", "-S"]  # -S 表示不用手动启动"开始"按钮
    sumoCmd = [sumoBinary] + sumoConfig
    traci.start(sumoCmd)  # 打开接口
    step = 0
    total_co2 = 0
    while step < 500:
        traci.simulationStep()
        if step % 20 == 0:
            # 获取当前仿真中所有车辆的ID
            vehicle_ids = traci.vehicle.getIDList()
            # 计算所有车辆的总CO2排放量
            total_co2 = sum(traci.vehicle.getCO2Emission(vid) for vid in vehicle_ids)
            logger.warning(f"当前时间: {step}, 总CO2排放量: {total_co2:.2f} mg/s, 车辆数量: {len(vehicle_ids)}")

        step += 1
        time.sleep(0.1)

    traci.close()
    logger.success('Done!')


# 调用方法
if __name__ == "__main__":
    # configure SUMO_HOME
    if 'SUMO_HOME' in os.environ:
        sumo_home = os.environ['SUMO_HOME']
        tools = os.path.join(sumo_home, 'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare environment variable 'SUMO_HOME'")
    
    sumoBinary = os.path.join(sumo_home, "bin", "sumo-gui")
    
    # 获取名称输入(最好具体)
    loc = input('Place Name: ')

    # 设置源路径和目标路径(需要修改)
    source = rf'C:\Users\huawei\Downloads\map.osm'
    path1=os.path.dirname(os.path.realpath(__file__))
    destination = path1 + '\\myMap\\map.osm'
    net_file  = path1 + '\\myMap\\map.net.xml'
    trips_file = path1 + '\\myMap\\map.rou.xml'
    sumocfgfile = path1 + '\\myMap\\map.sumocfg'

    # 调用下载并移动 OSM 文件的函数
    download_osm_file(loc, source, destination)
    convert_osm_to_net(destination, net_file)
    generate_random_trips(net_file, trips_file)
    sim(sumocfgfile)
