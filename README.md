# log-extractor

Background: https://docs.qq.com/doc/DQWlTalBOT3FKaG9T

1. Get Apache log file.
    - `cd data` and `make`.
    - You can get more dataset from [logpai/loghub](https://github.com/logpai/loghub).
2. Setup the Python environment.
    - Install [Rye](https://rye-up.com/).
    - `rye sync` and `source .venv/bin/activate`.
        - (Optional) Add the source command to `.envrc` and use [envrc-rs](https://github.com/chenyao36/envrc-rs).
3. Test.
    - `rye run cli diff`: compare the first and second halves of the original file.
    - `rye run cli diff data/Apache.shuf.part-1-of-2.log data/Apache.shuf.part-2-of-2.log`: compare the first and second halves of the shuffle.

