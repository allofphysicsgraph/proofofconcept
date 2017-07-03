from sys import argv
import ast
from astmonkey import visitors, transformers
f=open(argv[1])
node = ast.parse(f.read())
node = transformers.ParentNodeTransformer().visit(node)
visitor = visitors.GraphNodeVisitor()
visitor.visit(node)
visitor.graph.write_dot('test')
