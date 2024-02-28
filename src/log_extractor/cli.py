import click
from click import echo
from collections import Counter
import re
from pathlib import Path


TOKEN_PATTERN = re.compile(r'[a-zA-Z_](\.?[a-zA-Z0-9_]+)+')
ExistsFileType = click.Path(exists=True, dir_okay=False, path_type=Path)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', default=Path('data/Apache.log'), type=ExistsFileType)
@click.option('--topk', default=100, type=int)
def count(path, topk):
    counter = get_token_counter_from_path(path)
    for token, count in counter.most_common(topk):
        echo(f'{token}\t{count}')


@cli.command()
@click.argument('path_a', default=Path('data/Apache.part-1-of-2.log'), type=ExistsFileType)
@click.argument('path_b', default=Path('data/Apache.part-2-of-2.log'), type=ExistsFileType)
@click.option('--topk', default=100, type=int)
def diff(path_a, path_b, topk):
    counters = [
        get_token_counter_from_path(path_a),
        get_token_counter_from_path(path_b),
    ]
    merged_counter = {}
    for i, counter in enumerate(counters):
        for token, count in counter.most_common(topk):
            if token in merged_counter:
                merged_counter[token][i] = count
            else:
                counts = [ 0, 0 ]
                counts[i] = count
                merged_counter[token] = counts
    merged_items = sorted(
        merged_counter.items(),
        key=lambda _: (-max(*_[1]), _[0]),
    )
    for token, (count_a, count_b) in merged_items:
        echo(f'{token}\t{count_a}\t{count_b}')


def get_token_counter_from_path(path):
    token_counter = Counter()
    with path.open(mode='r') as handle:
        for ln, row in enumerate(handle):
            for match in TOKEN_PATTERN.finditer(row):
                token_counter[match.group(0)] += 1
    return token_counter

