import numpy
from nltk import CFG
from nltk.tree import Tree, Nonterminal


def cky_parsing(words: list, grammar: CFG, draw=False):
        n = len(words) + 1
        table = numpy.ndarray(shape=(n,n), dtype=set)

        for j in range(1, n):                                                           # Looping over the columns
            table[j-1, j] = list(map(lambda rule: Tree(rule.lhs(), [words[j-1]]),      # Filling the bottom cell
                                list(filter(lambda production: len(production.rhs()) == 1
                                                                  and production.rhs()[0] == words[j-1],
                                                               grammar.productions()))))

            for i in reversed(range(0, j-1)):
                for k in range(i+1, j):                         # Looping over the possible split locations between i and j
                    rule = list(map(lambda rule: Tree(rule.lhs(), [table[i, k][0], table[k, j][0]]),
                                list(filter(lambda production: len(production.rhs()) == 2
                                                                   and table[i, k] is not None and production.rhs()[0] in map(lambda head: head.label(), table[i, k])
                                                                   and table[k, j] is not None and production.rhs()[1] in map(lambda head: head.label(), table[k, j]),
                                                                grammar.productions()))))
                    table[i, j] = rule if table[i, j] is None else rule + table[i, j]

        if draw and len(table[0, n - 1]) != 0: table[0, n - 1][0].draw()
        return table[0, n-1][0] if (len(table[0, n-1]) != 0 and table[0, n-1][0].label() == Nonterminal("S")) else Tree("Grammar error", [])


def translate(tree: Tree, translation_rules: list, draw=False):
    put_left = list(filter(lambda i: isinstance(tree[i], Tree)
                                          and tree[i].label() in translation_rules
                                          and not 'put_left' in locals(),
                                tree.treepositions()))[0] if len(tree) != 0 else []

    if len(put_left) != 0:
        tree = apply_translation(put_left, tree)
        if tree[tree.treepositions()[-2]].label() not in [Nonterminal("AUX"), Nonterminal("VERB")]:
            tree = apply_translation(tree.treepositions()[-2], tree)
        if draw: tree.draw()

    return tree


def apply_translation(put_left, tree):
    prefix = tree.__getitem__(put_left)
    tree.__delitem__(put_left)
    tree = Tree(Nonterminal("S'"), [prefix, tree])
    return tree