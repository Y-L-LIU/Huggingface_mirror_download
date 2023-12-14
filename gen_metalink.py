# %%
import re
from tqdm import tqdm

# %%
import requests

# %%
# user, repo = "mistralai", "Mixtral-8x7B-Instruct-v0.1"
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("user_repo")
args = parser.parse_args()

user, repo = args.user_repo.split("/")

# %%
resp = requests.get(f"https://hf-mirror.com/{user}/{repo}/tree/main")
resp

# %%
filenames = re.findall(
    rf"/{user}/{repo}/resolve/main/([^\?]+)\?download=true", resp.text
)

filenames

# %%


import time

# resps = list()

# for fn in tqdm(filenames):
#     resps.append(
#             requests.get(
#                 "https://hf-mirror.com/{user}/{repo}/raw/main/{filename}".format(
#                 user=user, repo=repo, filename=fn
#             )
#         )
#     )
#     time.sleep(0.5)

# resps

resps = [
    requests.get(
        "https://hf-mirror.com/{user}/{repo}/raw/main/{filename}".format(
            user=user, repo=repo, filename=fn
        )
    )
    for fn in tqdm(filenames)
]
resps

# %%

hash_matches = [re.search(r"sha256:([a-z0-9]{64})", resp.text) for resp in resps]
hash_matches

# %%

verifies = [
    f"""
       <verification>
         <hash type="sha256">{m.group(1)}</hash>
       </verification>"""
    if m is not None
    else ""
    for m in hash_matches
]
verifies

# %%


# %%
files = "\n".join(
    [
        f"""
     <file name="{fn}">{verify}
       <resources>
         <url type="https">https://hf-mirror.com/{user}/{repo}/resolve/main/{fn}?download=true</url> 
       </resources>
     </file>"""
        for fn, verify in zip(filenames, verifies)
    ]
)

print(files)

# %%
with open(f"{repo}.metalink", "w", encoding="utf-8") as f:
    f.write(
        f"""<metalink version="3.0" xmlns="http://www.metalinker.org/">
   <files>{files}
   </files>
 </metalink>"""
    )

# %%
