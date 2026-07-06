class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

def reverse_inorder(node, arr):
    if node is None:
        return
    # Step 1: visita sottoalbero destro
    reverse_inorder(node.right, arr)

    # Step 2: visita il nodo corrente
    print(f"Visito nodo {node.key}")
    arr.append(node.key)
    print(f"Array aggiornato: {arr}\n")

    # Step 3: visita sottoalbero sinistro
    reverse_inorder(node.left, arr)

# Costruzione dell'albero BST
#           8
#         /   \
#        3     10
#       / \      \
#      1   6     14
#         / \    /
#        4   7  13

root = Node(8)
root.left = Node(3)
root.right = Node(10)

root.left.left = Node(1)
root.left.right = Node(6)
root.left.right.left = Node(4)
root.left.right.right = Node(7)

root.right.right = Node(14)
root.right.right.left = Node(13)

# Eseguiamo la visita reverse-inorder
arr = []
reverse_inorder(root, arr)

print("✅ Risultato finale, chiavi in ordine decrescente:")
print(arr)
