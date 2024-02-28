import click
from click import echo
from collections import Counter, defaultdict
import re
from typing import Set
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
@click.argument(
    'path_a', default=Path('data/Apache.part-1-of-2.log'), type=ExistsFileType
)
@click.argument(
    'path_b', default=Path('data/Apache.part-2-of-2.log'), type=ExistsFileType
)
@click.option('--topk', default=100, type=int)
@click.option('--context-size', default=20, type=int)
@click.option('--topk-for-each-context-size', default=20, type=int)
def diff(path_a, path_b, topk, context_size, topk_for_each_context_size):
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
                counts = [0, 0]
                counts[i] = count
                merged_counter[token] = counts
    merged_items = sorted(
        merged_counter.items(),
        key=lambda _: (-max(*_[1]), _[0]),
    )
    echo('Token Frequency'.center(50, '='))
    for token, (count_a, count_b) in merged_items:
        echo(f'{token}\t{count_a}\t{count_b}')
    echo('Token Transition'.center(50, '='))
    t1 = get_transition_from_path(
        path_a, vocab_set=merged_counter, context_size=context_size
    )
    t2 = get_transition_from_path(
        path_b, vocab_set=merged_counter, context_size=context_size
    )
    for size in range(1, context_size):
        echo('Token Transition [{}]'.format(size).center(50, '-'))
        context_maps = [t1[size], t2[size]]
        merged_counter = {}
        for i, context_map in enumerate(context_maps):
            for context, counter in context_map.items():
                if context in merged_counter:
                    merged_counter[context][i] = counter.total
                else:
                    counts = [0, 0]
                    counts[i] = counter.total
                    merged_counter[context] = counts
        merged_items = sorted(
            merged_counter.items(),
            key=lambda _: (-max(*_[1]), _[0]),
        )
        for context, (total_a, total_b) in merged_items[:topk_for_each_context_size]:
            echo(
                '{}\t{}\t{}\n... {}\t{}\t{}'.format(
                    ' '.join(context),
                    total_a,
                    (t1[size][context] if total_a else ''),
                    (
                        '{:.0f}% dist. simi.'.format(
                            t1[size][context].get_simi_with(t2[size][context]) * 100
                        )
                        if total_a and total_b
                        else 'N/A'
                    ),
                    total_b,
                    (t2[size][context] if total_b else ''),
                )
            )


def get_transition_from_path(path, *, vocab_set: Set[str], context_size: int):
    context = []
    counter_map = defaultdict(lambda: defaultdict(TransitionCounter))
    for token in iter_token_from_path(path):
        if token in vocab_set:
            if len(context) >= context_size:
                del context[0]
            for i in range(1, len(context) + 1):
                counter_map[i][tuple(context[-i:])].append(token)
            context.append(token)
    return counter_map


class TransitionCounter:
    def __init__(self):
        self.total = 0
        self.counter = Counter()

    def append(self, token):
        self.total += 1
        self.counter[token] += 1

    def __str__(self):
        threshold = round(self.total * 0.9)
        parts = []
        for token, count in self.counter.most_common():
            parts.append('{:3.0f}% {:10}'.format(count / self.total * 100, token))
            if threshold <= 0:
                break
        return ' | '.join(parts)

    def get_simi_with(self, other):
        val = 0
        for token, x in self.counter.items():
            y = other.counter.get(token)
            if y is not None:
                val += x * y
        return val / self.total / other.total


def get_token_counter_from_path(path):
    token_counter = Counter()
    for token in iter_token_from_path(path):
        token_counter[token] += 1
    return token_counter


def iter_token_from_path(path):
    with path.open(mode='r') as handle:
        for row in handle:
            for match in TOKEN_PATTERN.finditer(row):
                yield match.group(0)
