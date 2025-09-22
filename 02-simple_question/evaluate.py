import yaml
import os
import re

work_dir = os.path.dirname(__file__)

with open(os.path.join(work_dir, "answer.yaml"), "r") as f:
    data = yaml.safe_load(f)

ans_lst = []
for i in range(1,12):
    ans_lst.extend([str(i) for i in data[i]])

with open(os.path.join(work_dir, "template.txt"), "r") as f:
    template = f.read()

ans_iter = iter(ans_lst)

preview_char = re.sub(r"（\s+）",lambda x:f"（{next(ans_iter)}）",template)
print(preview_char)