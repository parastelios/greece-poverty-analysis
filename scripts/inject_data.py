import json
import re

with open("../output/report.html") as f:
    html = f.read()
with open("../output/report_data.json") as f:
    data = json.load(f)

new_line = "const DATA = " + json.dumps(data) + ";"
html_new, n = re.subn(r"const DATA = \{.*?\};", new_line, html, count=1, flags=re.DOTALL)
print("replacements made:", n)

with open("../output/report.html", "w") as f:
    f.write(html_new)
print("New DATA size:", len(json.dumps(data)), "bytes")
