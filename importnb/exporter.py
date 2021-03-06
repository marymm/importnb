
# coding: utf-8

# In[1]:


try:
    from .decoder import LineNoDecoder
except:
    from decoder import LineNoDecoder        
    
__file__ = globals().get('__file__', 'exporter.ipynb')


# # Compilation
# 
# Compilation occurs in the __3__ steps:
# 
# 1. Text is transformed into a valid source string.
# 2. The source string is parsed into an abstract syntax tree
# 3. The abstract syntax compiles to valid bytecode 

# In[2]:


__IPYTHON__ = False
try:
    from IPython import get_ipython
    if not get_ipython():
        raise ValueError("""There is no interactive IPython shell""")
    __IPYTHON__ = True
except: ...
    
if __IPYTHON__:
    try:
        from .compiler_ipython import Compiler, NotebookNode, NotebookExporter
    except:
        from compiler_ipython import Compiler, NotebookNode, NotebookExporter
else:
    try:
        from .compiler_python import Compiler, NotebookNode, NotebookExporter
    except:
        from compiler_python import Compiler, NotebookNode, NotebookExporter
        


# In[3]:


import ast, sys
from json import load, loads
from pathlib import Path
from dataclasses import dataclass


# In[4]:


@dataclass
class Code(NotebookExporter, Compiler):
    """An exporter than returns transforms a NotebookNode through the InputSplitter.
    
    >>> assert type(Code().from_filename(Path(__file__).with_suffix('.ipynb'))) is NotebookNode"""
    filename: str = '<module exporter>'
    name: str = '__main__'
    decoder: type = LineNoDecoder
        
    def __post_init__(self): NotebookExporter.__init__(self) or Compiler.__init__(self)
            
    def from_file(Code,file_stream, resources=None, **dict): 
        for str in ('name', 'filename'): setattr(Code, str, dict.pop(str, getattr(Code, str)))
        return Code.from_notebook_node(
            NotebookNode(**load(file_stream, cls=Code.decoder)), resources, **dict)
    
    def from_filename(Code,  filename, resources=None, **dict):
        Code.filename, Code.name = filename, Path(filename).stem
        return super().from_filename(filename, resources, **dict)

    def from_notebook_node(Code, nb, resources=None, **dict): 
        for cell in nb['cells']:
            if cell['cell_type'] == 'code':
                cell['source'] = Code.from_code_cell(cell, **dict)
        return nb
    
    def from_code_cell(Code, cell, **dict):  
        return Code.transform(cell['source'])


# In[5]:


class AST(Code):
    """An exporter than returns parsed ast.
    
    >>> assert type(AST().from_filename(Path(__file__).with_suffix('.ipynb'))) is ast.Module"""
    def from_notebook_node(AST, nb: NotebookNode, resource: dict=None, **dict):         
        return AST.ast_transform(ast.fix_missing_locations(ast.Module(body=sum((
            AST.ast_parse(
                AST.from_code_cell(cell, **dict), lineno=cell['metadata'].get('lineno', 1)
            ).body for cell in nb['cells'] if cell['cell_type']=='code'
        ), []))))


# In[6]:


class Compile(AST):
    """An exporter that returns compiled and cached bytecode.
    
    >>> assert Compile().from_filename(Path(__file__).with_suffix('.ipynb'))"""        
    def from_notebook_node(Compile, nb, resources: dict=None, **dict):
        return Compile.compile(super().from_notebook_node(nb, resources, **dict))


# In[7]:


if __name__ ==  '__main__':
    from pathlib import Path
    from nbconvert.exporters.script import ScriptExporter
    Path('exporter.py').write_text(ScriptExporter().from_filename('exporter.ipynb')[0])
    __import__('doctest').testmod()

