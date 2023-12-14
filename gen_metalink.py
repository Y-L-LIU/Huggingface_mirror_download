import re
from argparse import ArgumentParser

import requests
from tqdm import tqdm


def _main():
    parser = ArgumentParser()
    parser.add_argument("user_repo")
    parser.add_argument("--timeout", type=float, default=5)
    args = parser.parse_args()
    timeout = args.timeout
    user, repo = args.user_repo.split("/")

    resp = requests.get(f"https://hf-mirror.com/{user}/{repo}/tree/main")

    filenames = re.findall(
        rf"/{user}/{repo}/resolve/main/([^\?]+)\?download=true", resp.text
    )

    resps = [
        requests.get(
            "https://hf-mirror.com/{user}/{repo}/raw/main/{filename}".format(
                user=user, repo=repo, filename=fn
            )
        )
        for fn in tqdm(filenames)
    ]

    hash_matches = [re.search(r"sha256:([a-z0-9]{64})", resp.text) for resp in resps]

    verifies = [
        f"""
<verification>
    <hash type="sha256">{m.group(1)}</hash>
</verification>"""
        if m is not None
        else ""
        for m in hash_matches
    ]

    # %%
    files = "\n".join(
        [
            f"""<file name="{fn}">{verify}
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


if __name__ == "__main__":
    _main()
