# -*- coding: utf-8 -*-
with open("en/index.html", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace("<!-- 抖音Videos直播 -->", "<!-- Video Broadcast -->")
text = text.replace("Leading Active Ingredients 高效渗...", "Leading Active Ingredients High-Efficiency Penetration...")
text = text.replace("版权所有", "Copyright")
text = text.replace("粤ICP备2025368502号-1", "Guangdong ICP No. 2025368502-1")

with open("en/index.html", "w", encoding="utf-8") as f:
    f.write(text)

print("Cleaned!")
