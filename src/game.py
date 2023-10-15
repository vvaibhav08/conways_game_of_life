import pygame
import numpy as np

COLOR_DEAD_CELL = (200, 200, 225)
COLOR_ALIVE_CELL = (255, 255, 215)
COLOR_BACKGROUND = (10, 10, 40)
COLOR_GRID = (30, 30, 60)

GOL_PATTERNS = {
    "still": {
        "block": "2o$2o!",
        "beehive": "b2o$o2bo$b2o!",
        "loaf": "b2o$o2bo$bobo$2bob!",
    },
    "oscillators": {
        "blinkers": "3o!",
        "toad": "bo3bo$3o2b3o!",
        "beacon": "2o2b2o$2o2b2o!",
    },
    "spaceships": {
        "glider": "bob$2bo$3o!",
        "lwss": "",
        "weekender": "",
        "glider_duplicator": "",
        "r-pentomino": "5b$2b2ob$b2o2b$2bo2b$5b!",
    },
}

# map where on the grid the initial pattern will be placed
# in fractions of the total grid size
POSITION_TO_PIXEL_MAPPING = {
    "center": (0.5, 0.5),
    "top_left": (0.1, 0.1),
    "top_right": (0.9, 0.1),
    "bottom_left": (0.1, 0.9),
    "bottom_right": (0.9, 0.9),
}


class GAME:
    def __init__(self, pattern: str, grid_size: int, pattern_pos: str = "center", pixel_size: int = 8):
        self.grid_size = grid_size
        self.pixel_size = pixel_size
        self.pattern = pattern
        self.init_pattern_position = pattern_pos

    def create_init_pattern(self) -> np.array:
        grid = np.zeros((self.grid_size, self.grid_size))
        print(f"Given patttern is: {self.pattern}")
        if self.pattern != "random":
            # Find the RLE value of the subkey
            rle_value: str | None = None
            for category in GOL_PATTERNS.values():
                for subkey, value in category.items():
                    if subkey == self.pattern:
                        rle_value = value
                        break

            # Check if the subkey exists and retrieve the RLE value
            if rle_value is not None:
                print(f"RLE value for '{self.pattern}': {rle_value}")
                pattern_array = GAME._rle_decoder(pattern=rle_value)

                position = next(
                    value for key, value in POSITION_TO_PIXEL_MAPPING.items() if key == self.init_pattern_position
                )
                grid[
                    int(position[0] * pattern_array.shape[0]) : int(position[0] * pattern_array.shape[0])
                    + pattern_array.shape[0],
                    int(position[1] * pattern_array.shape[1]) : int(position[1] * pattern_array.shape[1])
                    + pattern_array.shape[1],
                ] = pattern_array
            else:
                print(f"'{self.pattern}' not found in the dictionary.")

        else:
            grid = np.random.randint(2, size=(grid.shape[0], grid.shape[1]))

        return grid

    def update(self, surface, cur):
        nxt = np.zeros((cur.shape[0], cur.shape[1]))

        for r, c in np.ndindex(cur.shape):
            num_alive = np.sum(cur[r - 1 : r + 2, c - 1 : c + 2]) - cur[r, c]

            if cur[r, c] == 1 and num_alive < 2 or num_alive > 3:
                col = COLOR_DEAD_CELL
            elif (cur[r, c] == 1 and 2 <= num_alive <= 3) or (cur[r, c] == 0 and num_alive == 3):
                nxt[r, c] = 1
                col = COLOR_ALIVE_CELL

            col = col if cur[r, c] == 1 else COLOR_BACKGROUND
            pygame.draw.rect(
                surface, col, (c * self.pixel_size, r * self.pixel_size, self.pixel_size - 1, self.pixel_size - 1)
            )

        return nxt

    def main(self):
        pygame.init()
        surface = pygame.display.set_mode((self.grid_size * self.pixel_size, self.grid_size * self.pixel_size))
        pygame.display.set_caption("John Conway's Game of Life")

        cells = self.create_init_pattern()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            surface.fill(COLOR_GRID)
            cells = self.update(surface, cells)
            pygame.display.update()

    @staticmethod
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
                    current_row.extend([1] * repeat_times)
                    repeat_times = 1
                elif char == "b":
                    current_row.extend([0] * repeat_times)
                    repeat_times = 1

            current_row.extend([0] * (max_pattern_width - len(current_row)))
            pattern_array.append(current_row)

        return np.array(pattern_array, dtype=np.int8)


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Conway's Game of Life with starting pattern.")
    parser.add_argument("startingpattern", type=str, help="Enter the starting pattern, e.g., 'glider'")
    args = parser.parse_args()

    game = GAME(pattern=args.startingpattern, grid_size=120)
    game.main()
