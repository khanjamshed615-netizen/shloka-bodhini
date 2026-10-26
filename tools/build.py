import re, json, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from translit import slp2dev, dev2slp, norm_key

SRC = '/home/claude/sanskrit-lexicon/csl-orig/v02'
AMARA = '/home/claude/sd/sa-head/sa-entries/amara-onto/amara-onto.babylon'
OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/claude/app/data'

def records(path):
    cur = None
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')
            if line.startswith('<L>'):
                m = re.search(r'<k1>([^<]*)', line)
                cur = [m.group(1), []]
            elif line.startswith('<LEND>'):
                if cur: yield cur[0], cur[1]
                cur = None
            elif cur is not None:
                cur[1].append(line)

def join_lines(lines):
    out = ''
    for ln in lines:
        ln = re.sub(r'^<(?:H|P|>|C\d+)>', '', ln).strip()
        ln = re.sub(r'\[Page[^\]]*\]', '', ln).strip()
        if not ln: continue
        if out.endswith('-') and not out.endswith('--'):
            out = out[:-1] + ln
        else:
            out = (out + ' ' + ln) if out else ln
    return out

def clean_deva_dict(lines):
    t = join_lines(lines)
    t = t.replace('{??}', '…')
    t = re.sub(r'<pic[^>]*>', '', t)
    t = re.sub(r'<[^>]+>', '', t)
    hw, _, body = t.partition('¦')
    body = body.strip(' ,')
    body = body.replace('..', '॥')
    body = re.sub(r'\s\.(?=\s|$)', ' ।', body)
    body = re.sub(r'(?<=[a-zA-Z~\'])\.', '।', body)
    # stored in SLP1 (1 byte/char) and converted to Devanagari in the browser
    body = re.sub(r"(?<=[A-Za-z~'])0", '॰', body)
    return hw.strip(), body

def clean_mw(lines):
    t = join_lines(lines)
    t = re.sub(r'<info[^>]*/>|<listinfo[^>]*/>', '', t)
    t = re.sub(r'<s>(.*?)</s>', lambda m: slp2dev(m.group(1)), t)
    t = re.sub(r'<ls[^>]*>(.*?)</ls>', r'\1', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('¦', '').strip()
    t = re.sub(r'\s+', ' ', t)
    return t

def clean_ap(lines):
    t = join_lines(lines)
    if '{{Lbody' in t: return None
    t = re.sub(r'\{#(.*?)#\}', lambda m: slp2dev(m.group(1)), t)
    t = re.sub(r'\{[%@](.*?)[%@]\}', r'\1', t)
    t = re.sub(r'<[^>]+>', '', t)
    t = t.replace('¦', ' —').strip()
    t = re.sub(r'\s+', ' ', t)
    return t

data = collections.defaultdict(lambda: collections.defaultdict(list))

for code, name in (('s', 'skd'), ('v', 'vcp')):
    n = 0
    for k1, lines in records(f'{SRC}/{name}/{name}.txt'):
        hw, body = clean_deva_dict(lines)
        if not body: continue
        data[norm_key(k1)][code].append([hw, body]); n += 1
    print(name, n)

n = 0
for k1, lines in records(f'{SRC}/mw/mw.txt'):
    t = clean_mw(lines)
    if t: data[norm_key(k1)]['m'].append(t); n += 1
print('mw', n)

n = 0
for k1, lines in records(f'{SRC}/ap90/ap90.txt'):
    t = clean_ap(lines)
    if t: data[norm_key(k1)]['a'].append(t); n += 1
print('ap90', n)

n = 0
with open(AMARA, encoding='utf-8') as f:
    blocks = f.read().split('\n\n')
for b in blocks:
    lines = b.strip().split('\n')
    if len(lines) < 2 or lines[0].startswith('#'): continue
    parts = [p.strip() for p in lines[1].split('<br><br>')]
    if len(parts) < 4: continue
    first = parts[0].split()
    hw = first[0]; g = ' '.join(first[1:]).strip('।')
    obj = {'h': hw, 'g': g, 'm': parts[1]}
    for p in parts[2:]:
        if p.startswith('समानार्थक:'):
            obj['syn'] = p.split(':', 1)[1]
        elif re.fullmatch(r'[\d।]+', p):
            obj['r'] = p
        elif 'पदार्थ-विभागः' in p:
            pass
        elif ' : ' in p:
            obj.setdefault('rel', []).append(p)
        elif '।' in p or '॥' in p:
            obj['v'] = p
    for h in lines[0].split('|'):
        key = norm_key(dev2slp(h.strip()))
        if key:
            data[key]['k'].append(obj); n += 1
print('amara', n)

# ---- sharding ----
keys = sorted(data)
print('keys', len(keys))
LIMIT = 350_000

def size_of(ks):
    return sum(len(json.dumps(data[k], ensure_ascii=False).encode()) + len(k) + 6 for k in ks)

shards = {}
def assign(prefix, ks, L):
    if size_of(ks) <= LIMIT or L >= 7:
        shards[prefix] = ks; return
    short = [k for k in ks if len(k) <= L]
    if short or prefix: shards[prefix] = short
    groups = collections.defaultdict(list)
    for k in ks:
        if len(k) > L: groups[k[:L+1]].append(k)
    for p, g in groups.items(): assign(p, g, L+1)

top = collections.defaultdict(list)
for k in keys: top[k[:1]].append(k)
for p, g in top.items(): assign(p, g, 1)

def fname(p):
    return ''.join((c.lower() + '2') if c.isupper() else c for c in p) or 'root'

os.makedirs(f'{OUT}/k', exist_ok=True)
for p, ks in shards.items():
    if not ks: continue
    with open(f'{OUT}/k/{fname(p)}.json', 'w', encoding='utf-8') as f:
        json.dump({k: data[k] for k in ks}, f, ensure_ascii=False, separators=(',', ':'))
with open(f'{OUT}/index.json', 'w') as f:
    json.dump(sorted(p for p, ks in shards.items() if ks), f, separators=(',', ':'))
print('shards', sum(1 for ks in shards.values() if ks))
