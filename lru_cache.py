import threading
import time
import random

class Node:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class ThreadSafeLRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be greater than 0")
        self.capacity = capacity
        self.cache = {}
        self.head = Node(None, None)
        self.tail = Node(None, None)
        self.head.next = self.tail
        self.tail.prev = self.head
        self.lock = threading.Lock()

    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                self._remove_node(node)
                self._add_to_front(node)
                return node.value
            return None

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                node = self.cache[key]
                node.value = value
                self._remove_node(node)
                self._add_to_front(node)
            else:
                if len(self.cache) >= self.capacity:
                    lru_node = self.tail.prev
                    self._remove_node(lru_node)
                    del self.cache[lru_node.key]
                new_node = Node(key, value)
                self.cache[key] = new_node
                self._add_to_front(new_node)

def simulation(cache, thread_id, num_ops):
    for _ in range(num_ops):
        op = random.choice(["get", "put"])
        key = random.randint(1, 100) # Assuming a smaller key space to trigger evictions
        if op == "get":
            cache.get(key)
        else:
            value = f"thread_{thread_id}_val_{key}"
            cache.put(key, value)
        time.sleep(0.001) # Small sleep to encourage thread interleaving

def validate_cache(cache):
    with cache.lock:
        # 1. Check size limits
        assert len(cache.cache) <= cache.capacity, f"Cache size {len(cache.cache)} exceeds capacity {cache.capacity}"

        # 2. Check linked list length vs dictionary length
        curr = cache.head.next
        list_len = 0
        keys_in_list = set()
        while curr != cache.tail:
            list_len += 1
            keys_in_list.add(curr.key)
            curr = curr.next

        assert list_len == len(cache.cache), f"List length {list_len} does not match dictionary size {len(cache.cache)}"

        # 3. Check keys in list match keys in dictionary
        assert keys_in_list == set(cache.cache.keys()), "Keys in linked list do not match keys in dictionary"

        # 4. Check reverse linked list iteration
        curr = cache.tail.prev
        reverse_len = 0
        while curr != cache.head:
            reverse_len += 1
            curr = curr.prev

        assert list_len == reverse_len, f"Forward length {list_len} does not match reverse length {reverse_len}"

        print(f"Validation successful. Cache size: {len(cache.cache)}")

if __name__ == "__main__":
    print("Starting LRU Cache Simulation...")
    cache_capacity = 50
    cache = ThreadSafeLRUCache(cache_capacity)
    num_threads = 5
    ops_per_thread = 1000

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=simulation, args=(cache, i, ops_per_thread))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("Simulation finished. Running validation checks...")
    validate_cache(cache)
