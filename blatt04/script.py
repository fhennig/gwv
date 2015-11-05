from sys import argv # filename as argument
from heapq import heappop, heappush # priority queue
import itertools as it # combinatorics

s_empty   = ' '
s_start   = 's'
s_goal    = 'g'
s_wall    = 'x'
s_path    = 'o'
s_visited = '.'
s_portal  = '0123456789'


def get_field(filename):
    """Läd das Spielfeld aus der angegebenen Datei in ein mehrdimensionales Array"""
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
    """Expandiert den gegebenen Pfad um 1, auf alle möglichen Nachbarpfade"""
    ns = neighbors(field, *path[-1])
    return [path + [n] for n in ns if is_walkable(field, *n)]


def search(field, dequeue_fn):
    """generische Suchfunktion, unterschiedliches Verhalten wird erzeugt
    indem unterschiedliche Strategien zum bestimmen des nächsten Pfades
    angegeben werden"""
    expand_counter = 0
    frontier_size_counter = 0
    v_matrix = visited_matrix(field)
    frontier = [[get_start(field)]]
    while len(frontier) != 0:
        path = dequeue_fn(frontier)
        if is_goal(field, *path[-1]):
            return path, v_matrix, expand_counter, frontier_size_counter
        if not is_discovered(v_matrix, *path[-1]):
            set_discovered(field, v_matrix, *path[-1])
            next_paths = get_next_paths(field, path)
            frontier += next_paths
            frontier_size_counter += len(next_paths)
            expand_counter += 1
    return [], v_matrix, expand_counter, frontier_size_counter


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


def est_dist_to_nearest_goal_with_portals(field, x, y):
    """Man muss alle wege zum allen zielen betrachten, in denen man durch
    jedes Portal entweder durchgeht oder nicht, und jede Reihenfolge der
    Portale. Anzahl der zu Testenden Pfade: |G| * 2^|P| * |P|!"""
    goals = get_goals(field)
    dists = []
    portal_seqs = []
    portal_coords = [get_portals(field, n) for n in s_portal]
    portal_coords = filter(lambda l: len(l) != 0, portal_coords)
    for perm in it.permutations(portal_coords): # Alle RHF der Portale
        for i in range(len(perm) + 1):
            for c in it.combinations(perm, i):  # Alle Möglichkeiten ein
                l = [[(x, y)]] + list(c) + [goals]
                dists.append(sum([min_dist(l[i-1], l[i]) for i in range(1, len(l))]))
    return min(dists)


# Problem: Berücksichtigt nur 1 Portal auf dem Pfad
def est_dist_to_nearest_goal(field, x, y):
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
    return len(path) + est_dist_to_nearest_goal(field, *path[-1])


def priority_with_portals(field, path):
    return len(path) + est_dist_to_nearest_goal_with_portals(field, *path[-1])


def a_star(field):
    expand_counter = 0
    frontier_size_counter = 0
    v_matrix = visited_matrix(field)
    frontier = []
    init_path = [get_start(field)]
    heappush(frontier, (priority_with_portals(field, init_path), init_path))
    while(len(frontier) != 0):
        _, path = heappop(frontier)
        if is_goal(field, *path[-1]):
            return path, v_matrix, expand_counter, frontier_size_counter
        if not is_discovered(v_matrix, *path[-1]):
            set_discovered(field, v_matrix, *path[-1])
            next_paths = get_next_paths(field, path)
            for p in next_paths:
                heappush(frontier, (priority_with_portals(field, p), p))
            frontier_size_counter += len(next_paths)
            expand_counter += 1
    return [], v_matrix, expand_counter, frontier_size_counter


# 1.  Als Heuristik verwenden wir die Manhattan-Distance, da diese in
#     unserer Umgebung eine bessere Abschätzung als die euklidische
#     Distanz darstellt.

# 2.  Ist die Frontier irgendwann leer, geben wir einen leeren Pfad
#     zurück. Der Algorithmus terminiert, findet aber keine Lösung, da
#     es auch keine Lösung gibt.


def path_to_string(field, v_matrix, path):
    """Gibt das Feld aus, mit dem gegebenen Pfad eingezeichnet"""
    str = ''
    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            if [x, y] in path and cell == s_empty:
                str += s_path
            elif v_matrix[y][x] and cell == s_empty:
                str += s_visited
            else:
                str += cell
    return str


def show_alg_info(field, alg):
    path, v_matrix, expand_counter, f_s_counter = alg(field)
    print(alg.__name__ + ":",
          "path length:", len(path),
          "expansions:", expand_counter,
          "frontier_size:", f_s_counter)
    print(path_to_string(field, v_matrix, path))
    

if __name__ == '__main__' and len(argv) == 2:
    # Aufruf über 'python <script-File> <Feld-File>' (Python 3)
    _, filename  = argv
    field = get_field(filename)
    show_alg_info(field, dfs)
    show_alg_info(field, bfs)
    show_alg_info(field, a_star)
