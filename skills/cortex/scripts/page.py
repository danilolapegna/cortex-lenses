#!/usr/bin/env python3
"""Render a complete Cortex run as one offline HTML page; never calls a model."""
import argparse
from html import escape
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from check import frontmatter

ROOT = Path(__file__).resolve().parents[1]
IDEA_FIELDS = ('id', 'title', 'lens', 'section', 'before', 'after', 'kept_intact',
               'mechanism', 'dependency', 'means', 'breaking_point', 'cheapest_test', 'drop_it_if')
OPTIONAL_IDEA = {'new_operation', 'variants', 'evidence', 'analogy'}
STRESS_FIELDS = ('idea_id', 'finding', 'cost', 'next_test', 'owner', 'stop_if')


def text_fields(obj, fields, label):
    if not isinstance(obj, dict):
        raise ValueError(f'{label}: expected an object')
    for key in fields:
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f'{label}: missing nonempty string {key}')


def only_fields(obj, allowed, label):
    extra = set(obj) - set(allowed)
    if extra:
        raise ValueError(f'{label}: unknown fields {sorted(extra)}; refusing to hide data')


def string_list(value, label):
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise ValueError(f'{label}: expected a list of nonempty strings')


def validate(run):
    text_fields(run, ('title', 'problem', 'baseline', 'independence'), 'run')
    only_fields(run, {'title', 'problem', 'baseline', 'independence', 'lens_results',
                      'ideas', 'selected', 'selection_note', 'stress_tests'}, 'run')
    lenses = {p.stem: frontmatter(p)[0] for p in (ROOT / 'lenses').glob('*.md')}
    for key in ('lens_results', 'ideas'):
        if not isinstance(run.get(key), list):
            raise ValueError(f'run: {key} must be a list')
    results = {}
    for row in run['lens_results']:
        text_fields(row, ('lens', 'status', 'note'), 'lens result')
        only_fields(row, {'lens', 'status', 'note'}, 'lens result')
        lens = row['lens']
        if lens not in lenses or lens in results or row['status'] not in {'ideas', 'none'}:
            raise ValueError(f'lens result: unknown, duplicate or invalid result for {lens}')
        results[lens] = row
    missing = {k for k, v in lenses.items() if v['core']} - set(results)
    if missing:
        raise ValueError('missing core lens results: ' + ', '.join(sorted(missing)))
    ids = set()
    used = set()
    for idea in run['ideas']:
        text_fields(idea, IDEA_FIELDS, 'idea')
        only_fields(idea, set(IDEA_FIELDS) | OPTIONAL_IDEA, 'idea')
        ident, lens = idea['id'], idea['lens']
        if ident in ids:
            raise ValueError(f'idea: duplicate id {ident}')
        ids.add(ident)
        if lens not in results or results[lens]['status'] != 'ideas':
            raise ValueError(f'{ident}: lens has no ideas result')
        used.add(lens)
        if idea['section'] not in {'ideas', 'premises', 'conditional'}:
            raise ValueError(f'{ident}: invalid section')
        if lenses[lens]['family'] == 'change-representation':
            text_fields(idea, ('new_operation',), ident)
        for key in ('new_operation', 'analogy'):
            if key in idea:
                text_fields(idea, (key,), ident)
        if lenses[lens]['family'] == 'transfer-a-mechanism':
            text_fields(idea, ('analogy',), ident)
        for key in ('variants', 'evidence'):
            if key in idea:
                string_list(idea[key], f'{ident}.{key}')
    if used != {k for k, v in results.items() if v['status'] == 'ideas'}:
        raise ValueError('an ideas result has no preserved card')
    selected = run.get('selected', [])
    string_list(selected, 'selected')
    if len(selected) != len(set(selected)) or set(selected) - ids:
        raise ValueError('selected: unknown or duplicate idea ID')
    if selected or 'selection_note' in run:
        text_fields(run, ('selection_note',), 'run')
    tests = run.get('stress_tests', [])
    if not isinstance(tests, list):
        raise ValueError('stress_tests must be a list')
    check_ids = {p.stem for p in (ROOT / 'checks').glob('*.md')}
    tested = set()
    for test in tests:
        text_fields(test, STRESS_FIELDS, 'stress test')
        only_fields(test, set(STRESS_FIELDS) | {'checks', 'review_steps'}, 'stress test')
        ident = test['idea_id']
        if ident not in selected or ident in tested:
            raise ValueError(f'{ident}: stress test requires a unique, explicitly selected idea')
        tested.add(ident)
        string_list(test.get('checks'), f'{ident}.checks')
        if not test['checks'] or set(test['checks']) - check_ids:
            raise ValueError(f'{ident}: missing or unknown checks')
        if 'review_steps' in test:
            steps = test['review_steps']
            if not isinstance(steps, list) or not steps:
                raise ValueError(f'{ident}: review_steps must be a nonempty list')
            seen = set()
            for step in steps:
                text_fields(step, ('check', 'finding', 'change'), 'review step')
                only_fields(step, {'check', 'finding', 'change'}, 'review step')
                if step['check'] not in test['checks'] or step['check'] in seen:
                    raise ValueError(f'{ident}: review step requires a unique applied check')
                seen.add(step['check'])
            if seen != set(test['checks']):
                raise ValueError(f'{ident}: each applied check needs a review step')
    return lenses


def prose(value):
    return escape(value).replace('\n', '<br>')


def definition(label, value):
    return f'<dt>{escape(label)}</dt><dd>{prose(value)}</dd>'


def details_list(label, values):
    if not values:
        return ''
    return f'<details><summary>{escape(label)} ({len(values)})</summary><ul>' + ''.join(
        '<li>' + prose(v) + '</li>' for v in values) + '</ul></details>'


# Simplified from the previous full-page layout: neutral paper, green accent,
# numbered cards and native disclosure. No tracking, remote fonts or script runtime.
CSS = '''
:root{--bg:#f6f5f1;--surface:#fff;--ink:#1d1c1a;--muted:#5d5a54;--line:#dcd8cf;--accent:#7a5f1c}
*{box-sizing:border-box}html{scroll-padding-top:1rem}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.65 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1040px;margin:auto;padding:40px 24px 80px}header{border-top:5px solid var(--accent);padding-top:24px}h1,h2,h3,h4{line-height:1.12;text-wrap:balance}h1{font:normal clamp(2.4rem,6vw,4.4rem)/1.06 Georgia,serif;max-width:17ch;margin:14px 0 24px}h2{font:normal 2rem/1.2 Georgia,serif;margin:42px 0 18px}h3{font:normal 1.65rem/1.2 Georgia,serif;margin:10px 0 20px}
p{max-width:72ch;margin:0 0 16px}.eyebrow,.meta{color:var(--accent);font-size:1rem;letter-spacing:.09em;text-transform:uppercase}.notice{border-left:3px solid var(--accent);padding:8px 18px;background:#f4eedd;color:var(--ink)}a{color:var(--accent);text-underline-offset:4px}nav a{display:inline-flex;align-items:center;min-height:44px}nav{display:flex;flex-wrap:wrap;gap:12px 24px;padding:20px 0;border-block:1px solid var(--line);margin:28px 0}article{border:1px solid var(--line);border-radius:10px;padding:26px;background:var(--surface);margin:18px 0;break-inside:avoid}article:target{outline:3px solid var(--accent);outline-offset:3px}.number{font-variant-numeric:tabular-nums;color:var(--muted);font-size:.9rem}
.shift{display:grid;grid-template-columns:1fr 1fr;gap:22px;border-block:1px solid var(--line);padding:18px 0;margin-bottom:18px}.shift b{display:block;color:var(--muted);font-size:1rem;text-transform:uppercase;letter-spacing:.06em}.shift p{margin:6px 0 0}dl{margin:0}dt{font-size:1rem;color:var(--accent);font-weight:650;margin-top:14px}dd{margin:2px 0 0}details{border-top:1px solid var(--line);padding-top:12px;margin-top:18px}summary{cursor:pointer;min-height:44px;display:list-item;padding:7px 0;font-weight:600}li{margin:10px 0}a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:4px}footer{margin-top:42px;border-top:1px solid var(--line);padding-top:20px;color:var(--muted)}.coverage li{padding-bottom:12px;border-bottom:1px solid var(--line)}.coverage strong{display:block}p,dd,li,h1,h2,h3,h4{overflow-wrap:anywhere}.empty{color:var(--muted)}
.review-step{border-top:1px solid var(--line);margin-top:22px;padding-top:16px}.review-step h4{font-size:1.1rem;color:var(--accent);margin:0 0 12px}.review-step .shift{border:0;margin:0;padding:0}.stress-card{border-top:4px solid var(--accent)}
@media(max-width:600px){.wrap{padding:24px 16px 48px}article{padding:20px}.shift{grid-template-columns:1fr;gap:16px}h2{font-size:1.65rem}}
@media print{body{background:white;font-size:11pt}.wrap{max-width:none;padding:0}nav{display:none}article{border-radius:0}details{display:block}details::details-content{content-visibility:visible}h1{font-size:32pt}}
'''


def render(run):
    lenses = validate(run)
    cards = run['ideas']
    selected = set(run.get('selected', []))
    by_id = {card['id']: card for card in cards}
    check_names = {p.stem: frontmatter(p)[0]['name'] for p in (ROOT / 'checks').glob('*.md')}
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width,initial-scale=1">',
             '<title>' + escape(run['title']) + ' · Cortex</title><style>' + CSS + '</style></head>',
             '<body><main class="wrap"><header><p class="eyebrow">Cortex / Full exploration</p>',
             '<h1>' + prose(run['title']) + '</h1><p>' + prose(run['problem']) + '</p>',
             '<p class="notice">' + prose(run['independence']) + '</p></header>',
             '<nav aria-label="Page sections"><a href="#baseline">Baseline</a><a href="#ideas">All ideas (' + str(len(cards)) + ')</a><a href="#coverage">Lens coverage</a><a href="#selection">Selection &amp; stress</a></nav>',
             '<section id="baseline"><h2>The competent, obvious answer</h2><p>' + prose(run['baseline']) + '</p></section>']
    order = {idea['id']: i for i, idea in enumerate(cards, 1)}
    labels = [('kept_intact', 'Kept intact'), ('new_operation', 'New operation it enables'),
              ('cheapest_test', 'Cheapest test'), ('drop_it_if', 'Drop it if')]
    deep = [('mechanism', 'Mechanism'), ('dependency', 'Decisive dependency'),
            ('means', 'Available means'), ('breaking_point', 'Breaking point'), ('analogy', 'Analogy and its limit')]
    for section, title in [('ideas', 'All ideas'), ('premises', 'Premises worth reopening'), ('conditional', 'Conditional routes')]:
        section_cards = [x for x in cards if x['section'] == section]
        parts.append(f'<section id="{section}"><h2>{title}</h2>')
        if not section_cards:
            parts.append('<p class="empty">No ideas in this section.</p>')
        for card in section_cards:
            anchor = 'idea-' + str(order[card['id']])
            parts.extend([f'<article id="{anchor}">',
                          '<span class="number">' + f'{order[card["id"]]:02d}' + ' / ' + escape(card['id']) + (' · Selected' if card['id'] in selected else '') + '</span>',
                          '<h3>' + prose(card['title']) + '</h3><p class="meta">' + escape(lenses[card['lens']]['name']) + '</p>',
                          '<div class="shift"><div><b>Before</b><p>' + prose(card['before']) + '</p></div><div><b>After</b><p>' + prose(card['after']) + '</p></div></div><dl>'])
            parts += [definition(label, card[key]) for key, label in labels if key in card]
            parts.append('</dl><details><summary>How it could work</summary><dl>')
            parts += [definition(label, card[key]) for key, label in deep if key in card]
            parts.append('</dl></details>')
            parts.append(details_list('Variants kept intact', card.get('variants', [])))
            parts.append(details_list('Evidence and limits', card.get('evidence', [])))
            parts.append('</article>')
        parts.append('</section>')
    parts.append('<section id="coverage"><h2>Every lens accounted for</h2><details><summary>Inspect ' + str(len(run['lens_results'])) + ' lens results</summary><ul class="coverage">')
    for row in run['lens_results']:
        parts.append('<li><strong>' + escape(lenses[row['lens']]['name']) + ' · ' + escape(row['status']) + '</strong>' + prose(row['note']) + '</li>')
    parts.append('</ul></details></section><section id="selection"><h2>Selection &amp; stress</h2>')
    if not selected:
        parts.append('<p>No ideas selected. Stress testing waits for an explicit choice.</p>')
    else:
        parts.append('<p class="notice">' + prose(run['selection_note']) + '</p><ul>')
        parts.extend('<li><a href="#idea-' + str(order[x]) + '">' + escape(by_id[x]['title']) + '</a></li>' for x in run['selected'])
        parts.append('</ul>')
        if not run.get('stress_tests'):
            parts.append('<p>Selected ideas have not been stress-tested yet.</p>')
    for test in run.get('stress_tests', []):
        ident = test['idea_id']
        parts.append('<article class="stress-card"><p class="eyebrow">After selection / ' +
                     str(order[ident]).zfill(2) + '</p><h3>' + prose(by_id[ident]['title']) + '</h3>')
        parts.append('<p><a href="#idea-' + str(order[ident]) + '">Revisit the original proposal</a></p><dl>')
        parts.append(definition('Checks applied', ', '.join(check_names[x] for x in test['checks'])))
        parts.append(definition('Strongest objection', test['finding']))
        parts.append('</dl>')
        for step in test.get('review_steps', []):
            parts.append('<section class="review-step"><h4>' + escape(check_names[step['check']]) +
                         '</h4><div class="shift"><div><b>What the check reveals</b><p>' +
                         prose(step['finding']) + '</p></div><div><b>What changes</b><p>' +
                         prose(step['change']) + '</p></div></div></section>')
        parts.append('<dl>')
        parts.extend(definition(label, test[key]) for key, label in
                     [('cost', 'Cost and uncertainty'), ('next_test', 'Revised next test'),
                      ('owner', 'Who would act'), ('stop_if', 'Stop or revise if')])
        parts.append('</dl></article>')
    parts.append('</section><footer>All cards and conditions are preserved. An idea is a proposal to test, never permission to act.</footer></main></body></html>')
    return ''.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    try:
        run = json.loads(args.run.read_text(encoding='utf-8'))
        result = render(run)
        if args.out.resolve() == args.run.resolve():
            raise ValueError('output must not overwrite the run JSON')
        args.out.write_text(result, encoding='utf-8')
    except (OSError, ValueError) as exc:
        print(f'FAIL: {exc}', file=sys.stderr)
        return 1
    print(f'PASS: {args.out} · {len(run["ideas"])} ideas · {len(run["lens_results"])} lens results')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
