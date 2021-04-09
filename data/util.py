from tqdm import tqdm
from pathlib import Path

Path.ls = lambda x : [o.name for o in x.iterdir()]
Path.ls_p = lambda x : [str(o) for o in x.iterdir()]
Path.str = lambda x : str(x)

to_path = lambda p :  p if isinstance(p, Path) else Path(p)

