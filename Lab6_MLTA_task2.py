from typing import List


class TrieNode:
    def __init__(self):
        self.children = {}
        self.value = None


class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.word_count = 0

    def put(self, key, value=None):
        if not isinstance(key, str) or not key:
            raise TypeError("Key must be a non-empty string")
        current = self.root
        for char in key:
            if char not in current.children:
                current.children[char] = TrieNode()
            current = current.children[char]
        if current.value is None:
            self.word_count += 1
        current.value = value

    def get(self, key):
        if not isinstance(key, str) or not key:
            raise TypeError("Key must be a non-empty string")
        current = self.root
        for char in key:
            if char not in current.children:
                return None
            current = current.children[char]
        return current.value


class Homework(Trie):
    @staticmethod
    def _check(text, name):
        if not isinstance(text, str):
            raise TypeError(f"{name} must be a string")
        if not text:
            raise ValueError(f"{name} must be a non-empty string")

    def _collect(self, node, prefix, words):
        if node.value is not None:
            words.append(prefix)
        for char in sorted(node.children):
            self._collect(node.children[char], prefix + char, words)

    def _find_node(self, prefix):
        current = self.root
        for char in prefix:
            if char not in current.children:
                return None
            current = current.children[char]
        return current

    def count_words_with_suffix(self, pattern) -> int:
        self._check(pattern, "pattern")
        words = []
        self._collect(self.root, "", words)
        return sum(1 for word in words if word.endswith(pattern))

    def has_prefix(self, prefix) -> bool:
        self._check(prefix, "prefix")
        node = self._find_node(prefix)
        if node is None:
            return False
        words = []
        self._collect(node, prefix, words)
        return len(words) > 0

    def autocomplete(self, prefix) -> List[str]:
        self._check(prefix, "prefix")
        node = self._find_node(prefix)
        if node is None:
            return []
        result = []
        stack = [(node, prefix)]
        while stack and len(result) < 3:
            current, word = stack.pop()
            if current.value is not None:
                result.append(word)
            for char in sorted(current.children, reverse=True):
                stack.append((current.children[char], word + char))
        return result

    def size(self) -> int:
        count = 0
        stack = [self.root]
        while stack:
            node = stack.pop()
            for child in node.children.values():
                count += 1
                stack.append(child)
        return count


if __name__ == "__main__":
    trie = Homework()
    words = ["apple", "application", "banana", "cat"]
    for i, word in enumerate(words):
        trie.put(word, i)

    assert trie.count_words_with_suffix("e") == 1
    assert trie.count_words_with_suffix("ion") == 1
    assert trie.count_words_with_suffix("a") == 1
    assert trie.count_words_with_suffix("at") == 1

    assert trie.has_prefix("app") == True
    assert trie.has_prefix("bat") == False
    assert trie.has_prefix("ban") == True
    assert trie.has_prefix("ca") == True

    assert trie.count_words_with_suffix("E") == 0
    assert trie.has_prefix("App") == False

    assert trie.autocomplete("app") == ["apple", "application"]
    assert trie.autocomplete("b") == ["banana"]
    assert trie.autocomplete("dog") == []
    assert trie.size() == 21

    trie2 = Homework()
    for i, word in enumerate(["cart", "care", "car", "careful", "cat", "card", "dog"]):
        trie2.put(word, i)
    assert trie2.autocomplete("car") == ["car", "card", "care"]
    assert trie2.autocomplete("ca") == ["car", "card", "care"]
    assert trie2.autocomplete("cat") == ["cat"]
    assert trie2.size() == 13
    assert Homework().size() == 0

    for method, bad in [(trie.has_prefix, 123), (trie.count_words_with_suffix, None),
                        (trie.autocomplete, ["a"]), (trie.has_prefix, "")]:
        try:
            method(bad)
            assert False
        except (TypeError, ValueError):
            pass

    print("Слова у дереві:", words)
    print("count_words_with_suffix('e') =", trie.count_words_with_suffix("e"))
    print("count_words_with_suffix('ion') =", trie.count_words_with_suffix("ion"))
    print("count_words_with_suffix('a') =", trie.count_words_with_suffix("a"))
    print("count_words_with_suffix('at') =", trie.count_words_with_suffix("at"))
    print("has_prefix('app') =", trie.has_prefix("app"))
    print("has_prefix('bat') =", trie.has_prefix("bat"))
    print("has_prefix('ban') =", trie.has_prefix("ban"))
    print("has_prefix('ca') =", trie.has_prefix("ca"))
    print("autocomplete('app') =", trie.autocomplete("app"))
    print("size() =", trie.size())
    print()
    print("Слова у дереві:", ["cart", "care", "car", "careful", "cat", "card", "dog"])
    print("autocomplete('car') =", trie2.autocomplete("car"))
    print("autocomplete('ca') =", trie2.autocomplete("ca"))
    print("size() =", trie2.size())
    print()
    try:
        trie.has_prefix(123)
    except TypeError as e:
        print("has_prefix(123) ->", type(e).__name__ + ":", e)
    try:
        trie.autocomplete("")
    except ValueError as e:
        print("autocomplete('') ->", type(e).__name__ + ":", e)
    print("\nУсі тести пройдено успішно!")