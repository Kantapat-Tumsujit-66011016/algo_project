import pygame
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 450
GRID_SIZE = 3  # You can change this to 3, 5, etc., for different grid sizes
TILE_SIZE = SCREEN_WIDTH // GRID_SIZE
FONT = pygame.font.Font(None, 40)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
FPS = 60

# Create a screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Sliding Puzzle')

# Create a new puzzle by shuffling tiles
def generate_puzzle():
    puzzle = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]  # Generate tiles 1 to n-1 and a blank tile (0)
    random.shuffle(puzzle)

    # Ensure the puzzle is solvable by checking its inversions (optional)
    while not is_solvable(puzzle):
        random.shuffle(puzzle)

    return puzzle

# Check if the puzzle is solvable
def is_solvable(puzzle):
    inversions = 0
    flat_puzzle = [tile for tile in puzzle if tile != 0]
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] > flat_puzzle[j]:
                inversions += 1
    return inversions % 2 == 0

# Draw the puzzle on the screen
def draw_puzzle(puzzle, moving_tile=None, move_offset=(0, 0), turns=0):
    screen.fill(WHITE)

    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            tile = puzzle[i * GRID_SIZE + j]
            if tile != 0:
                tile_rect = pygame.Rect(j * TILE_SIZE, i * TILE_SIZE, TILE_SIZE, TILE_SIZE)

                # If it's the moving tile, apply the move offset to its position
                if moving_tile and (i, j) == moving_tile:
                    tile_rect.move_ip(move_offset)

                pygame.draw.rect(screen, BLUE, tile_rect)
                text = FONT.render(str(tile), True, WHITE)
                screen.blit(text, (tile_rect.x + TILE_SIZE // 3, tile_rect.y + TILE_SIZE // 3))

    # Draw the "Start" button
    pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH // 3, SCREEN_HEIGHT - 40, SCREEN_WIDTH // 3, 30))
    start_text = FONT.render("Start", True, WHITE)
    screen.blit(start_text, (SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT - 35))

    # Draw the turn count
    turns_text = FONT.render(f"Turns: {turns}", True, BLACK)
    screen.blit(turns_text, (10, SCREEN_HEIGHT - 35))

# Move the tile with a swipe transition
def move_tile_with_animation(puzzle, row, col, clock):
    blank_index = puzzle.index(0)
    blank_row, blank_col = divmod(blank_index, GRID_SIZE)

    # Check if the clicked tile is adjacent to the blank tile
    if abs(blank_row - row) + abs(blank_col - col) == 1:
        # Calculate the direction of movement
        direction = (blank_row - row, blank_col - col)
        moving_tile = (row, col)

        # Perform the animation
        frames = 10  # Number of frames for the animation
        for frame in range(frames):
            move_offset = (direction[1] * TILE_SIZE * (frame + 1) / frames,
                           direction[0] * TILE_SIZE * (frame + 1) / frames)
            draw_puzzle(puzzle, moving_tile, move_offset)  # Removed the `turns` argument here
            pygame.display.flip()
            clock.tick(FPS)

        # After the animation, swap the clicked tile with the blank tile
        puzzle[blank_row * GRID_SIZE + blank_col], puzzle[row * GRID_SIZE + col] = (
            puzzle[row * GRID_SIZE + col], puzzle[blank_row * GRID_SIZE + blank_col])

        return True  # Movement happened
    return False  # No movement happened

# Check if the puzzle is solved
def is_solved(puzzle):
    return puzzle == list(range(1, GRID_SIZE * GRID_SIZE)) + [0]

# Main game loop
def main():
    clock = pygame.time.Clock()
    running = True
    puzzle = generate_puzzle()  # Initialize a random puzzle
    turns = 0  # Initialize turn counter

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if the "Start" button is clicked
                if SCREEN_WIDTH // 3 < mouse_x < 2 * SCREEN_WIDTH // 3 and SCREEN_HEIGHT - 40 < mouse_y < SCREEN_HEIGHT:
                    puzzle = generate_puzzle()  # Generate a new random puzzle
                    turns = 0  # Reset turn counter when new puzzle is generated

                # Check if a tile is clicked to move
                elif mouse_y < SCREEN_HEIGHT - 50:  # Exclude clicks on the "Start" button
                    row = mouse_y // TILE_SIZE
                    col = mouse_x // TILE_SIZE
                    if move_tile_with_animation(puzzle, row, col, clock):
                        turns += 1  # Increment turn count after a successful move

        draw_puzzle(puzzle, turns=turns)

        # Check if the puzzle is solved
        if is_solved(puzzle):
            # Draw a "You Win" message
            win_text = FONT.render("You Win!", True, GREEN)
            screen.blit(win_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == '__main__':
    main()
