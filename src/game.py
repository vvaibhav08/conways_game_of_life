import pygame
import numpy as np

COLOR_DEAD_CELL = (200, 200, 225)
COLOR_ALIVE_CELL = (255, 255, 215)
COLOR_BACKGROUND = (10, 10, 40)
COLOR_GRID = (30, 30, 60)

GOL_PATTERNS = {
    "still": {
        "block": "2o$2o!",
        "beehive": "b2o$o2bo$2bobo$o2bo$2o!",
        "loaf": "b2o$o2bo$obbo$o2bo$2o!",
    },
    "oscillators": {
        "blinkers": "3o!",
        "toad": "bo3bo$3o2b3o!",
        "beacon": "2o2b2o$2o2b2o!",
    },
    "spaceships": {
        "glider": "bo$2o$o!",
        "lwss": "b2o$4o$4o$o4b$2b3o2b$3bo2bo$o2bo$bo2bo!",
        "weekender": "2bo$o2b$4o$o4b$2b3o2b$3bo2bo$o2bo$bo2bo!",
    },
}

def _rle_decoder(pattern: str) -> np.array: 
    rows = pattern.split("$")
    pattern_array = []
    max_pattern_width = max([len(row) for row in rows])
    print(f"rows: {rows}")
    for row in rows:
        current_row = []
        repeat_times = 1
        for char in row:
            if char.isdigit():
                repeat_times = int(char)
            elif char == "o":
                current_row.extend([1]*repeat_times)
                repeat_times = 1
            elif char == "b":
                current_row.extend([0]*repeat_times)
                repeat_times = 1
            
        current_row.extend([0]*(max_pattern_width - len(current_row)))
        pattern_array.append(current_row)

    return np.array(pattern_array, dtype=np.int8)

def create_init_pattern(pattern: str, grid_size: tuple, position: str = "center") -> np.array:
    grid = np.zeros((grid_size[0], grid_size[1]))
    # Find the RLE value of the subkey
    rle_value = None
    for category in GOL_PATTERNS.values():
        for subkey, value in category.items():
            if subkey == pattern:
                rle_value = value
                break

    # Check if the subkey exists and retrieve the RLE value
    if rle_value is not None:
        print(f"RLE value for '{pattern}': {rle_value}")
    else:
        print(f"'{pattern}' not found in the dictionary.")

    pattern_array = _rle_decoder(pattern=rle_value)
    print(pattern_array)
    if position == "center":
        # grid midpoint
        pos = (3,3)
        grid[pos[0]:pos[0]+pattern_array.shape[0], pos[1]:pos[1]+pattern_array.shape[1]] = pattern_array        
    return grid

def update(surface, cur, sz):
    nxt = np.zeros((cur.shape[0], cur.shape[1]))

    for r, c in np.ndindex(cur.shape):
        num_alive = np.sum(cur[r-1:r+2, c-1:c+2]) - cur[r, c]

        if cur[r, c] == 1 and num_alive < 2 or num_alive > 3:
            col = COLOR_DEAD_CELL
        elif (cur[r, c] == 1 and 2 <= num_alive <= 3) or (cur[r, c] == 0 and num_alive == 3):
            nxt[r, c] = 1
            col = COLOR_ALIVE_CELL

        col = col if cur[r, c] == 1 else COLOR_BACKGROUND
        pygame.draw.rect(surface, col, (c*sz, r*sz, sz-1, sz-1))

    return nxt

def main(dimx, dimy, cellsize, pattern):
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("John Conway's Game of Life")

    cells = create_init_pattern(pattern, (dimx, dimy))
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(COLOR_GRID)
        cells = update(surface, cells, cellsize)
        pygame.display.update()

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Conway's Game of Life with starting pattern.")
    parser.add_argument("startingpattern", type=str, help="Enter the starting pattern, e.g., 'glider'")
    args = parser.parse_args()

    main(120, 90, 8, args.startingpattern)