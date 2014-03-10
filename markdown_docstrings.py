import os
import inspect

import markdown

md_converter = markdown.Markdown(extensions=['toc', 'def_list'])

class ModuleDocs(object):

    def __init__(self, module):
        self.module = module

    @property
    def html(self):
        return md_converter.convert(self.md)

    @property
    def md(self):
        _md = "#{module_name}\n[TOC]\n\n".format(module_name=self.module.__name__)
        _md += self._concat_md()
        return _md

    @property
    def bare_md(self):
        _md = ""
        _md += self._concat_md()
        return _md   

    def _add_header(self, obj):
        header = '##' + obj.__name__  + "\n\n" 
        if obj.__doc__:
            return header + inspect.cleandoc(obj.__doc__)
        else:
            return header + 'TODO: write documentation!'

    def _concat_md(self):
        docstrings = ''
        for name, obj in inspect.getmembers(self.module, inspect.isclass):
            docstrings += self._add_header(obj)
            docstrings += '\n\n'
        return docstrings


class PackageDocs(object):

    def __init__(self, package_name, doc_dir="docs"):
        self.package = __import__(package_name)
        self.doc_dir = doc_dir
        self.ref_index = os.path.join(doc_dir, 'ref-index.{ext}')
        self.modules = inspect.getmembers(self.package, inspect.ismodule)

    @property
    def index_md(self):
        _index_md = "#Reference: {package_name}\n\n".format(
                        package_name=self.package.__name__)
        for mname, mod in self.modules:
            _index_md += ' - [{module_name}]({filename})\n'.format(
                            module_name=mname,
                            filename=self._module_filename(mname,'html'))

        return _index_md + '\n\n'

    @property
    def index_html(self):
        return md_converter.convert(self.index_md)

    @property
    def md(self):
        _md = "#Reference: {package_name}\n\n[TOC]\n".format(
                        package_name=self.package.__name__)
        for mname, mod in self.modules:
            mdocs = ModuleDocs(mod)
            _md += mdocs.bare_md

        return _md

    @property
    def html(self):
        return md_converter.convert(self.md)

    def write_all(self, mtype='md'):
        with open(self.ref_index.format(ext=mtype), 'w') as fout:
            fout.write(getattr(self, 'index_'+mtype))

        for mname, mod in self.modules:
            loc = os.path.join(self.doc_dir, 
                               self._module_filename(mname, mtype))
            with open(loc, 'w') as fout:
                mdocs = ModuleDocs(mod)
                fout.write(getattr(mdocs,mtype))
            
    def _module_filename(self, module_name, ext):
        return 'ref-{module_name}.{ext}'.format(module_name=module_name,
                                                ext=ext)


if __name__ == '__main__':
    from tasks import download

    mdocs = ModuleDocs(download)

    with open('docs/module_test.html','w') as fout:
        fout.write(mdocs.html)
    
    with open('docs/module_test.md','w') as fout:
        fout.write(mdocs.md)

    PackageDocs('tasks').write_all('html')
    
    PackageDocs('tasks').write_all('md')

    with open('docs/ref-onepage.md','w') as fout:
        fout.write(PackageDocs('tasks').md)
    
    with open('docs/ref-onepage.html','w') as fout:
        fout.write(PackageDocs('tasks').html)
