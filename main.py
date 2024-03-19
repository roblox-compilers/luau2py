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
    elif type == 'AstExprBinary':
        op = None
        if node['op'] == 'Add':
            op = ast.Add()
        elif node['op'] == 'Sub':
            op = ast.Sub()
        elif node['op'] == 'Mul':
            op = ast.Mult()
        elif node['op'] == 'Div':
            op = ast.Div()
        elif node['op'] == 'Mod':
            op = ast.Mod()
        elif node['op'] == 'Pow':
            op = ast.Pow()
        elif node['op'] == 'Concat':
            op = ast.Add()
            if node['left']['type'] != 'AstExprConstantString':
                node['left']['type'] = 'AstExprConstantString'
                node['left']['value'] = str(node['left']['value'])
            if node['right']['type'] != 'AstExprConstantString':
                node['right']['type'] = 'AstExprConstantString'
                node['right']['value'] = str(node['right']['value'])
        elif node['op'] == 'Eq':
            op = ast.Eq()
        elif node['op'] == 'Ne':
            op = ast.NotEq()
        elif node['op'] == 'Lt':
            op = ast.Lt()
        elif node['op'] == 'Le':
            op = ast.LtE()
        elif node['op'] == 'Gt':
            op = ast.Gt()
        elif node['op'] == 'Ge':
            op = ast.GtE()
        elif node['op'] == 'And':
            op = ast.And()
        elif node['op'] == 'Or':
            op = ast.Or()
        else:
            print(f"Unhandled operator: {node['op']}")
            exit(1)

        if nested:
            return ast.BinOp(left=visit(node['left'], True), op=op, right=visit(node['right'], True))
        else:
            tree.append(ast.BinOp(left=visit(node['left'], True), op=op, right=visit(node['right'], True)))
    elif type == 'AstExprConstantNumber':
        if nested:
            return ast.Constant(n=node['value'])
        else:
            tree.append(ast.Constant(n=node['value']))
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