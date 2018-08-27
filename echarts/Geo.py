# coding=utf-8
from pyecharts import Geo
if __name__ == '__main__':

    data = [
        ("香洲区", 9),("金湾区", 12),("招远", 12),("舟山", 12),("齐齐哈尔", 14),("盐城", 15),
       ]

    geo = Geo(
        "全国主要城市空气质量",
        "data from pm2.5",
        title_color="#fff",
        title_pos="center",
        width=1200,
        height=600,
        background_color="#404a59",
    )
    attr, value = geo.cast(data)
    geo.add(
        "",
        attr,
        value,
        maptype="珠海",
        visual_range=[0, 200],
        visual_text_color="#fff",
        symbol_size=15,
        is_visualmap=True,
        is_piecewise=True,
        visual_split_number=6,
    )
    geo.render()