from sys import argv
from time import time
from heapq import heappop, heappush

s_start   = 's'
s_goal    = 'g'
s_wall    = 'x'
s_path    = 'o'
s_visited = '.'
s_portal  = '0123456789'

# Läd das Spielfeld aus der angegebenen Datei in ein mehrdimensionales Array
def get_field(filename):
    with open(filename) as f:
        return f.readlines()

def visited_matrix(field):
    return [[False for cell in row] for row in field]

def get_positions(field, chars):
    return sum([[(x, y) for x, char in enumerate(row)
                 if char in chars]
                for y, row in enumerate(field)], [])

def get_start(field):
    """Gibt die Startposition als [x, y] zurück"""
    return get_positions(field, s_start)[0]

def get_goals(field):
    """Gibt eine Liste aller Zielkoordinaten auf dem Feld zurück"""
    return get_positions(field, s_goal)
        
def is_goal(field, x, y):
    return field[y][x] == s_goal

def get_portals(field, number):
    return get_positions(field, number)

def is_portal(field, x, y):
    return field[y][x] in s_portal

def is_walkable(field, x, y):
    return field[y][x] != s_wall

def is_discovered(v_matrix, x, y):
    return v_matrix[y][x]

def set_discovered(field, v_matrix, x, y):
    if is_portal(field, x, y):
        coords = get_portals(field, field[y][x])
    else:
        coords = [(x, y)]
    for x, y in coords:
        v_matrix[y][x] = True

def four_neighbors(field, x, y):
    """Vierer-Nachbarschaft"""
    return [[x + 1, y],
            [x, y + 1],
            [x - 1, y],
            [x, y - 1]]

def neighbors(field, x, y):
    """Gibt die Nachbarn zu einem gegebenen Feld zurück, normalerweise 4
Nachbarn, bei Portalen auch mehr."""
    if is_portal(field, x, y):
        coords = get_portals(field, field[y][x])
    else:
        coords = [(x, y)]
    return sum([four_neighbors(field, *coord) for coord in coords], [])
    

def get_next_paths(field, path):
    ns = neighbors(field, *path[-1])
    return [path + [n] for n in ns if is_walkable(field, *n)]

# generische Suchfunktion, unterschiedliches Verhalten wird erzeugt
# indem unterschiedliche Strategien zum bestimmen des nächsten Pfades
# angegeben werden
def search(field, dequeue_fn):
    expand_counter = 0
    v_matrix = visited_matrix(field)
    frontier = [[get_start(field)]]
    while len(frontier) != 0:
        path = dequeue_fn(frontier)
        if is_goal(field, *path[-1]):
            return (path, v_matrix, expand_counter)
        if not is_discovered(v_matrix, *path[-1]):
            set_discovered(field, v_matrix, *path[-1])
            frontier += get_next_paths(field, path)
            expand_counter += 1
    return ([], v_matrix, expand_counter)

def dfs(field):
    return search(field, lambda l: l.pop()) # top des stacks entfernen

def bfs(field):
    return search(field, lambda l: l.pop(0)) # erstes element der queue entfernen

# A star

def manhattan_distance(x1, y1, x2, y2):
    """Manhattan Abstand, definiert für die Heuristik"""
    return abs(x2 - x1) + abs(y2 - y1)

def min_dist(start_list, goal_list):
    """Gibt die kürzeste Distanz zwischen irgendeinem Punkt aus der ersten
und irgendeinem Punkt aus der zweiten Liste zurück"""
    return min([manhattan_distance(xs, ys, xg, yg)
                for xs, ys in start_list
                for xg, yg in goal_list])
            

def estimate_distance_to_nearest_goal(field, x, y):
    dists = [] # Liste mit möglichen kürzesten Pfaden
    goals = get_goals(field)
    for p_number in s_portal:
        portals = get_portals(field, p_number)
        if len(portals) != 0:
            dists.append(min_dist([(x, y)], portals) + # kürzester Weg vom Start zu irgend einem Portal
                         min_dist(portals, goals))     # kürzester Weg von irgend einem Portal zu irgend einem Ziel
    dists.append(min_dist([(x, y)], goals))
    return min(dists)

                 
def priority(field, path):
    return len(path) + estimate_distance_to_nearest_goal(field, *path[-1])

def a_star(field):
    expand_counter = 0
    v_matrix = visited_matrix(field)
    frontier = []
    init_path = [get_start(field)]
    heappush(frontier, (priority(field, init_path), init_path))
    while(len(frontier) != 0):
        _, path = heappop(frontier)
        if is_goal(field, *path[-1]):
            return (path, v_matrix, expand_counter)
        if not is_discovered(v_matrix, *path[-1]):
            set_discovered(field, v_matrix, *path[-1])
            for p in get_next_paths(field, path):
                heappush(frontier, (priority(field, p), p))
            expand_counter += 1
    return ([], v_matrix, expand_counter)

# 1.  Als Heuristik verwenden wir die Manhattan-Distance, da diese in
#     unserer Umgebung eine bessere Abschätzung als die euklidische
#     Distanz darstellt.

# 2.  Ist die Frontier irgendwann leer, geben wir einen leeren Pfad
#     zurück. Der Algorithmus terminiert, findet aber keine Lösung, da
#     es auch keine Lösung gibt.



# Gibt das Feld aus, mit dem gegebenen Pfad eingezeichnet
def path_to_string(field, v_matrix, path):
    str = ''
    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            if [x, y] in path[1:-1]:
                str += s_path
            elif v_matrix[y][x] and cell == ' ':
                str += s_visited
            else:
                str += cell
    return str

def show_alg_info(field, alg):
    s_time = time()
    path, v_matrix, expand_counter = alg(field)
    e_time = time()
    duration = e_time - s_time
    visited_nodes = len(sum([[b for b in row if b] for row in v_matrix], []))
    print(alg.__name__, expand_counter, "expansions", visited_nodes, "visited nodes")
    print(path_to_string(field, v_matrix, path))
    



if __name__ == '__main__' and len(argv) == 2:
    # Aufruf über 'python <script-File> <Feld-File>' (Python 3)
    _, filename  = argv
    field = get_field(filename)
    show_alg_info(field, dfs)
    show_alg_info(field, bfs)
    show_alg_info(field, a_star)
