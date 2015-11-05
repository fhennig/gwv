from sys import argv
import time
from collections import deque

s_start = 's'
s_goal  = 'g'
s_wall  = 'x'

# Aufruf über 'python <script-File> <Feld-File>' (Python 3)
script, filename  = argv

# Läd das Spielfeld aus der angegebenen Datei in ein mehrdimensionales Array
def get_field(filename):
    with open(filename) as f:
        return [[[character, False] for character in line]
                for line in f.readlines()]

# Gibt das Feld aus, mit dem gegebenen Pfad eingezeichnet
def print_path(field, path):
    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            if [x, y] in path[1:-1]:
                print('o', end='')
            else:
                print(cell[0], end='')

# Gibt die Startposition als [x, y] zurück
def get_start(field):
    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            if cell[0] == s_start:
                return [x, y]
    
def is_goal(field, coords):
    x, y = coords
    return field[y][x][0] == s_goal

def is_walkable(field, coords):
    x, y = coords
    return field[y][x][0] != s_wall

def is_discovered(field, coords):
    x, y = coords
    return field[y][x][1]

def set_discovered(field, coords):
    x, y = coords
    field[y][x][1] = True

# Gibt die Vierer-Nachbarn zu einem gegebenen Feld zurück    
def neighbors(field, coords):
    x, y = coords
    return [[x + 1, y],
            [x, y + 1],
            [x - 1, y],
            [x, y - 1]]

def get_next_paths(field, path):
    ns = neighbors(field, path[-1])
    return [path + [n] for n in ns if is_walkable(field, n)]

# generische Suchfunktion, unterschiedliches Verhalten wird erzeugt
# indem unterschiedliche Strategien zum bestimmen des nächsten Pfades
# angegeben werden
def search(field, dequeue_fn):
    frontier = [[get_start(field)]]
    while len(frontier) != 0:
        path = dequeue_fn(frontier)
        if is_goal(field, path[-1]):
            return path
        if not is_discovered(field, path[-1]):
            set_discovered(field, path[-1])
            frontier = frontier + get_next_paths(field, path)

def dfs(field):
    return search(field, lambda l: l.pop()) # top des stacks entfernen

def bfs(field):
    return search(field, lambda l: l.pop(0)) # erstes element der queue entfernen

field1 = get_field(filename)
start_time1 = time.time()
p1 = dfs(field1)
end_time1 = time.time()
duration1 = end_time1 - start_time1

field2 = get_field(filename)
start_time2 = time.time()
p2 = bfs(field2)
end_time2 = time.time()
duration2 = end_time2 - start_time2

print("DFS-Path:", duration1 * 10**3, "ms")
print_path(field1, p1)
print()
print("BFS-Path:", duration2 * 10**3, "ms")
print_path(field2, p2)
print()
print("BFS/DFS:", duration2 / duration1)
