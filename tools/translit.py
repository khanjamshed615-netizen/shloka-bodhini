"""SLP1 <-> Devanagari conversion (build-time)."""
import re

VOW = {'a':('अ',''),'A':('आ','ा'),'i':('इ','ि'),'I':('ई','ी'),'u':('उ','ु'),'U':('ऊ','ू'),
       'f':('ऋ','ृ'),'F':('ॠ','ॄ'),'x':('ऌ','ॢ'),'X':('ॡ','ॣ'),'e':('ए','े'),'E':('ऐ','ै'),
       'o':('ओ','ो'),'O':('औ','ौ')}
CON = {'k':'क','K':'ख','g':'ग','G':'घ','N':'ङ','c':'च','C':'छ','j':'ज','J':'झ','Y':'ञ',
       'w':'ट','W':'ठ','q':'ड','Q':'ढ','R':'ण','t':'त','T':'थ','d':'द','D':'ध','n':'न',
       'p':'प','P':'फ','b':'ब','B':'भ','m':'म','y':'य','r':'र','l':'ल','v':'व','S':'श',
       'z':'ष','s':'स','h':'ह','L':'ळ'}
OTH = {'M':'ं','H':'ः','~':'ँ',"'":'ऽ'}
VIRAMA = '्'

def slp2dev(s):
    s = re.sub(r"[/\\^]", "", s)
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in CON:
            out.append(CON[c])
            nx = s[i+1] if i+1 < n else ''
            if nx in VOW:
                out.append(VOW[nx][1]); i += 2; continue
            out.append(VIRAMA); i += 1; continue
        if c in VOW:
            out.append(VOW[c][0])
        elif c in OTH:
            out.append(OTH[c])
        elif c == '0' and ''.join(out[-2:])[-1:] and 'ऀ' <= ''.join(out[-2:])[-1:] <= 'ॿ':
            out.append('॰')
        else:
            out.append(c)
        i += 1
    return ''.join(out)

R_VOW = {v[0]:k for k,v in VOW.items()}
R_MAT = {v[1]:k for k,v in VOW.items() if v[1]}
R_CON = {v:k for k,v in CON.items()}
R_OTH = {v:k for k,v in OTH.items()}

def dev2slp(s):
    s = s.replace('़', '')  # nukta
    out = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c in R_CON:
            out.append(R_CON[c])
            nx = s[i+1] if i+1 < n else ''
            if nx == VIRAMA: i += 2; continue
            if nx in R_MAT: out.append(R_MAT[nx]); i += 2; continue
            out.append('a'); i += 1; continue
        if c in R_VOW: out.append(R_VOW[c])
        elif c in R_OTH: out.append(R_OTH[c])
        elif c == 'ॐ': out.append('oM')
        else: out.append(c)
        i += 1
    return ''.join(out)

LETTERS = set(''.join(VOW) + ''.join(CON) + 'MH')

def norm_key(k):
    """Normalise an SLP1 headword: letters only, drop final visarga/anusvara."""
    k = ''.join(ch for ch in k if ch in LETTERS)
    if len(k) > 1 and k[-1] in 'HM':
        k = k[:-1]
    return k
