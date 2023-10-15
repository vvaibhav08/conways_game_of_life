const COLOR_DEAD_CELL = [200, 200, 225];
const COLOR_ALIVE_CELL = [255, 255, 215];
const COLOR_BACKGROUND = [10, 10, 40];
const COLOR_GRID = [30, 30, 60];

const GOL_PATTERNS = {
  still: {
    block: '2o$2o!',
    beehive: 'b2o$o2bo$b2o!',
    loaf: 'b2o$o2bo$bobo$2bob!',
  },
  oscillators: {
    blinkers: '3o!',
    toad: 'bo3bo$3o2b3o!',
    beacon: '2o2b2o$2o2b2o!',
  },
  spaceships: {
    glider: 'bob$2bo$3o!',
    lwss: '',
    weekender: '',
    glider_duplicator: '',
    rPentomino: '5b$2b2ob$b2o2b$2bo2b$5b!',
  },
};

function rleDecoder(pattern: string): np.array {
  const rows = pattern.split('$');
  const patternArray: number[][] = [];
  const maxPatternWidth = Math.max(...rows.map((row) => row.length));

  for (const row of rows) {
    const currentRow: number[] = [];
    let repeatTimes = 1;

    for (const char of row) {
      if (!isNaN(parseInt(char))) {
        repeatTimes = parseInt(char);
      } else if (char === 'o') {
        currentRow.push(...Array(repeatTimes).fill(1));
        repeatTimes = 1;
      } else if (char === 'b') {
        currentRow.push(...Array(repeatTimes).fill(0));
        repeatTimes = 1;
      }
    }

    currentRow.push(...Array(maxPatternWidth - currentRow.length).fill(0));
    patternArray.push(currentRow);
  }

  return np.array(patternArray, 'int8');
}

function createInitPattern(pattern: string, gridSize: [number, number], position: string = 'center'): np.array {
  const grid = np.zeros(gridSize);
  if (pattern !== 'random') {
    // Find the RLE value of the subkey
    let rleValue = null;

    for (const category of Object.values(GOL_PATTERNS)) {
      for (const subkey of Object.keys(category)) {
        if (subkey === pattern) {
          rleValue = category[subkey];
          break;
        }
      }
      if (rleValue) break;
    }

    // Check if the subkey exists and retrieve the RLE value
    if (rleValue) {
      console.log(`RLE value for '${pattern}': ${rleValue}`);
    } else {
      console.log(`'${pattern}' not found in the dictionary.`);
    }

    const patternArray = rleDecoder(rleValue);
    if (position === 'center') {
      const pos = [3, 3]; // grid midpoint
      grid.set(
        patternArray,
        new np.Range([pos[0], pos[0] + patternArray.shape[0]], [pos[1], pos[1] + patternArray.shape[1]])
      );
    }
  } else {
    grid.random_integers(2, { high: 2 });
  }
  return grid;
}

function update(surface: pygame.Surface, cur: np.array, sz: number): np.array {
  const nxt = np.zeros([cur.shape[0], cur.shape[1]]);

  for (const [r, c] of np.ndindex(cur.shape)) {
    const numAlive = np.sum(cur.slice([r - 1, r + 2], [c - 1, c + 2])) - cur.get(r, c);
    let col = COLOR_DEAD_CELL;

    if (cur.get(r, c) === 1 && (numAlive < 2 || numAlive > 3)) {
      col = COLOR_DEAD_CELL;
    } else if (
      (cur.get(r, c) === 1 && numAlive >= 2 && numAlive <= 3) ||
      (cur.get(r, c) === 0 && numAlive === 3)
    ) {
      nxt.set(1, r, c);
      col = COLOR_ALIVE_CELL;
    }

    col = cur.get(r, c) === 1 ? COLOR_ALIVE_CELL : COLOR_BACKGROUND;
    pygame.draw.rect(surface, col, [c * sz, r * sz, sz - 1, sz - 1]);
  }

  return nxt;
}

function main(cellDim: number, cellSize: number, pattern: string): void {
  pygame.init();
  const surface = pygame.display.set_mode([cellDim * cellSize, cellDim * cellSize]);
  pygame.display.set_caption("John Conway's Game of Life");

  const cells = createInitPattern(pattern, [cellDim, cellDim]);

  while (true) {
    for (const event of pygame.event.get()) {
      if (event.type === pygame.QUIT) {
        pygame.quit();
        return;
      }
    }

    surface.fill(COLOR_GRID);
    const newCells = update(surface, cells, cellSize);
    newCells.copyto(cells);
    pygame.display.update();
  }
}

if (require.main === module) {
  import { ArgumentParser } from 'argparse';

  const parser = new ArgumentParser({ description: "Conway's Game of Life with starting pattern." });
  parser.add_argument('startingpattern', { type: String, help: "Enter the starting pattern, e.g., 'glider'" });
  const args = parser.parse_args();

  main(120, 8, args.startingpattern);
}
