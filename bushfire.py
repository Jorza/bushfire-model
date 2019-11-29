def strings_to_grid(row_strings, expected_length):
    out_list = []
    for row in row_strings:
        row = row.strip().split(",")
        row = [int(item) for item in row]
        if len(row) != expected_length:
            return
        out_list.append(row)
    return out_list


def parse_scenario(filename):
    wind_directions = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']
    inf_dic = {
        "f_grid": [],
        "h_grid": [],
        "i_threshold": None,
        "w_direction": None,
        "burn_seeds": []
        }
    fp = open(filename)

    inf_list = fp.readlines()

    dimension = int(inf_list[0])
    if dimension <= 0:
        return

    inf_dic["f_grid"] = strings_to_grid(inf_list[1:dimension + 1], dimension)
    inf_dic["h_grid"] = strings_to_grid(inf_list[dimension + 1:2 * dimension + 1], dimension)

    i_threshold = int(inf_list[2 * dimension + 1])
    if i_threshold <= 0 or i_threshold > 8:
        return
    inf_dic["i_threshold"] = i_threshold

    w_direction = inf_list[2*dimension + 2].strip()
    if w_direction not in wind_directions:
        return
    inf_dic["w_direction"] = w_direction

    burn_strings = inf_list[2*dimension + 3:]
    burn_seeds = []
    for line in burn_strings:
        line = line.strip()
        if len(line) != 3:
            return
        i_coord = int(line[0])
        j_coord = int(line[2])
        line_tuple = (i_coord, j_coord)
        if inf_dic["f_grid"][i_coord][j_coord] == 0:
            return
        burn_seeds.append(line_tuple)
    inf_dic["burn_seeds"] = burn_seeds

    fp.close()
    return inf_dic


def get_wind_cells(w_direction, i, j):
    wind_cells = []

    wind_cells_n = [(i - 2, j - 1), (i - 2, j), (i - 2, j + 1)]
    wind_cells_w = [(i - 1, j - 2), (i, j - 2), (i + 1, j - 2)]
    wind_cells_nw = [(i - 1, j - 2), (i - 2, j - 2), (i - 2, j - 1)]
    if w_direction == "N":
        wind_cells = wind_cells_n
    elif w_direction == "W":
        wind_cells = wind_cells_w
    elif w_direction == "S":
        wind_cells = [(-1 - cell[0], cell[1]) for cell in wind_cells_n]
    elif w_direction == "E":
        wind_cells = [(cell[0], -1 - cell[1]) for cell in wind_cells_w]

    elif w_direction == "NW":
        wind_cells = wind_cells_nw
    elif w_direction == "NE":
        wind_cells = [(-1 - cell[0], cell[1]) for cell in wind_cells_nw]
    elif w_direction == "SW":
        wind_cells = [(cell[0], -1 - cell[1]) for cell in wind_cells_nw]
    elif w_direction == "SE":
        wind_cells = [(-1 - cell[0], -1 - cell[1]) for cell in wind_cells_nw]

    return wind_cells


def get_adjacent_cells(dimension, i, j, w_direction):
    adjacent_cells = []
    for i_new in range(i-1, i+2):
        if i_new < 0 or i_new >= dimension:
            continue
        for j_new in range(j-1, j+2):
            if j_new < 0 or j_new >= dimension:
                continue
            if i_new == i and j_new == j:
                continue
            adjacent_cells.append((i_new, j_new))
    wind_cells = get_wind_cells(w_direction, i, j)
    for cell in wind_cells:
        i_new = cell[0]
        j_new = cell[1]
        if i_new < 0 or i_new >= dimension or j_new < 0 or j_new >= dimension:
            continue
        adjacent_cells.append(cell)
    return adjacent_cells


def get_ignition_factor(adjacent_cells, b_grid, f_grid, h_grid, i, j):
    ignition_factor = 0
    if b_grid[i][j] or f_grid[i][j] == 0:
        return ignition_factor

    target_height = h_grid[i][j]
    for i_adj, j_adj in adjacent_cells:
        if not b_grid[i_adj][j_adj]:
            continue
        current_height = h_grid[i_adj][j_adj]
        if current_height < target_height:
            ignition_factor += 2
        elif current_height == target_height:
            ignition_factor += 1
        else:
            ignition_factor += 0.5
    return ignition_factor


def check_ignition(b_grid, f_grid, h_grid, i_threshold, w_direction, i, j):
    dimension = len(f_grid)
    adjacent_cells = get_adjacent_cells(dimension, i, j, w_direction)
    ignition_factor = get_ignition_factor(adjacent_cells, b_grid, f_grid, h_grid, i, j)
    return ignition_factor >= i_threshold


def is_burning(b_grid):
    for i in range(len(b_grid)):
        for j in range(len(b_grid)):
            if b_grid[i][j]:
                return True
    return False


def run_model(f_grid, h_grid, i_threshold, w_direction, burn_seeds):
    dimension = len(f_grid)

    b_grid_row = [0] * dimension
    b_grid = []
    for idx in range(dimension):
        b_grid.append(b_grid_row[:])
    for seed_x, seed_y in burn_seeds:
        b_grid[seed_x][seed_y] = 1

    cells_burnt = 0

    while is_burning(b_grid):
        for i in range(dimension):
            for j in range(dimension):
                if b_grid[i][j]:
                    f_grid[i][j] -= 1
                if check_ignition(b_grid, f_grid, h_grid, i_threshold, w_direction, i, j):
                    b_grid[i][j] = 1
                if b_grid[i][j] and f_grid[i][j] == 0:
                    b_grid[i][j] = 0
                    cells_burnt += 1

    return cells_burnt, f_grid


if __name__ == '__main__':
    inf_dic = parse_scenario('bf.txt')
    print(inf_dic["f_grid"])

    cells_burnt, f_grid = run_model(*inf_dic.values())
    print(f_grid)
