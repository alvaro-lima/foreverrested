"""Read installed QuestieDB Forever CBOR metadata as data; execute no addon code."""
import base64, hashlib, re, struct
from pathlib import Path

def cbor(data):
    pos=0
    def take(n):
        nonlocal pos
        b=data[pos:pos+n];pos+=n
        if len(b)!=n:raise ValueError('Truncated CBOR')
        return b
    def read():
        first=take(1)[0];major,ai=first>>5,first&31
        if major==7:
            if ai in (20,21):return ai==21
            if ai in (22,23):return None
            if ai in (25,26,27):return struct.unpack({25:'>e',26:'>f',27:'>d'}[ai],take({25:2,26:4,27:8}[ai]))[0]
            raise ValueError('Unsupported CBOR simple value')
        n=ai if ai<24 else int.from_bytes(take({24:1,25:2,26:4,27:8}[ai]),'big')
        if major==0:return n
        if major==1:return -1-n
        if major==2:return take(n)
        if major==3:return take(n).decode('utf-8')
        if major==4:return [read() for _ in range(n)]
        if major==5:return {read():read() for _ in range(n)}
        raise ValueError('Unsupported CBOR major type')
    result=read()
    if pos!=len(data):raise ValueError('Trailing CBOR bytes')
    return result

class InstalledDB:
    def __init__(self,path,expected_flavor='Forever'):
        self.path=Path(path)
        raw=self.path.read_bytes()
        self.sha256=hashlib.sha256(raw).hexdigest()
        self.meta=dict(re.findall(r'^## ([^:]+):\s*(.*?)\r?$',raw.decode('utf-8-sig'),re.M))
        if self.meta.get('X-Flavor')!=expected_flavor or self.meta.get('X-Mode')!='baked':raise ValueError(f'Expected installed baked {expected_flavor} database')
    def stored(self,key):
        value=self.meta.get(key)
        if value and re.fullmatch(r'~\d+~',value):value=''.join(self.meta[f'{key}-{i}'] for i in range(1,int(value[1:-1])+1))
        return value
    def entity(self,kind,identity):
        prefix=f'X-{kind}-{identity}-'
        scalar=self.stored(prefix+'S')
        if not scalar:return {}
        out=cbor(base64.b64decode(scalar))
        for key in self.meta:
            field=key.removeprefix(prefix)
            if key.startswith(prefix) and field.isdigit():
                value=self.stored(key)
                out[int(field)]=cbor(base64.b64decode(value))
        def clean(v):
            if isinstance(v,bytes):return v.decode('utf-8')
            if isinstance(v,list):return [clean(x) for x in v]
            if isinstance(v,dict):return {clean(k):clean(x) for k,x in v.items()}
            return v
        out=clean(out)
        out.pop('p',None)
        return out
