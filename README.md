# SUMO-Traci 基于OSM自动生成交通流
基于[原项目](https://github.com/psk1998/SUMO-TraCI_OSM)的改动
## 1. 下载osm文件
在运行script的时候，需要输入一个地点（最好是具体的,最好保持具体，例如 - 纽约市、卡内基梅隆大学等）然后使用drssionpage下载osm文件到source，需要修改destination到您指定的文件

## 2. 转换osm文件为net文件
使用netconvert命令将osm文件转换为net文件

## 3. 生成随机车辆
使用randomTrips.py命令生成随机车辆

## 4. 运行sumo-traci
TraCI 用于模拟 .sumocfg 文件，输出存储在 .out.xml 格式文件中
