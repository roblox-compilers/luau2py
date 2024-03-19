import astunparse
import ast
import subprocess
import sys
import json

tree = [
]

def tree2code(tree):
    return astunparse.unparse(ast.Module(body=tree))
def visit(node,nested=False):
    type = node['type']
    if type == 'AstStatBlock':
        visitBlock(node)
    elif type == 'AstExprError':
        print("Syntax error")
        exit(1)
    elif type == 'AstStatExpr':
        tree.append(ast.Expr(value=visit(node['expr'], True)))
    elif type == 'AstExprCall':
        if nested:
            return ast.Call(func=visit(node['func'], True), args=[visit(x, True) for x in node['args']], keywords=[])
        else:
            tree.append(ast.Call(func=visit(node['func'], True), args=[visit(x, True) for x in node['args']], keywords=[]))
    elif type == 'AstExprGlobal':
        if nested:
            return ast.Name(id=node['global'], ctx=ast.Load())
        else:
            tree.append(ast.Name(id=node['global'], ctx=ast.Load()))
    elif type == 'AstExprConstantString':
        if nested:
            return ast.Constant(s=node['value'])
        else:
            tree.append(ast.Constant(s=node['value']))
    else:
        print(f"Unhandled type: {type}")
        print(node)
        exit(1)
def visitBlock(node):
    for i in node['body']:
        visit(i)
def main():
    # Input
    fileIn = sys.argv[1]

    # AST
    ast = subprocess.run(["luau-ast", fileIn], capture_output=True).stdout.decode()
    ast_json = json.loads(ast)['root']
    print(ast_json)
    visitBlock(ast_json)
    print(tree)
    compiled = tree2code(tree)

    # Output
    fileOut = sys.argv[2]
    with open(fileOut, "w") as f:
        f.write(compiled)
if __name__ == '__main__':
    main()