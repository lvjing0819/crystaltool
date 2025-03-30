import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "/System/Library/Fonts/Supplemental/Songti.ttc"  # macOS 示例，Windows 可用 C:/Windows/Fonts/simhei.ttf
font_prop = fm.FontProperties(fname=font_path)

plt.pie([30, 40, 30], labels=['苹果', '香蕉', '橙子'], autopct='%1.1f%%', textprops={'fontproperties': font_prop})
plt.title('水果比例', fontproperties=font_prop)
plt.show()