# hf-mirror-download

Generate metalink file to weight files in huggingface repo from HTML responses.
Endpoint defaults to `hf-mirror.com`.

## Prerequisites

```sh
pip install requests
conda install aria2 -c conda-forge
```

## Example

```sh
python gen_metalink.py facebook/opt-125m -O opt-125m.metalink

mkdir ./opt-125m

# -V for sha256 checksum 
aria2c -M opt-125m.metalink -d ./opt-125m -V verification
```