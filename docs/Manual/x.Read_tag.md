把有name但没有name:zh标签的点，设置name:zh为name的值。

Find Nodes with name but no name:zh, set name:zh to the name.

```python
from kqs.waifu import Waifu

# 从.osm文件加载Waifu对象
# Read Waifu Object from .osm file
waifu = Waifu()
waifu.read_file("./demo.osm")

# 遍历所有点
# Iterate over all Nodes
for node in waifu.node_dict.values():
    # 跳过无name或有name:zh标签的点
    # Skip Nodes not tagged name or name:zh
    if "name" not in node.tags or "name:zh" in node.tags:
        continue

    # 获取name，并设置name:zh
    # Get name, and set name:zh
    name = node.tags["name"]
    node.tags["name:zh"] = name

    # 如果修改前后的标签有差异，则打印差异
    # Print difference if tags changed
    if node.has_tag_diff():
        node.print_diff()

# 写到.osm文件
# Write to .osm file
waifu.write("../demo_changed.osm")
```