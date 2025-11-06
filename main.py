import os
import sys
import time
import random

if os.name == "nt":
    import msvcrt
else:
    import termios, tty, select

WIDTH = 100
HEIGHT = 45


def get_key():
    if os.name == "nt":
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                return key.decode("utf-8").lower()
            except UnicodeDecodeError:
                return None
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1).lower()
    return None


def init_linux():
    if os.name != "nt":
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        return old_settings
    return None


def reset_linux(old_settings):
    if os.name != "nt" and old_settings:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)


def draw(snake, apples, score):
    print("\033[H", end="")
    frame = []
    frame.append(f"Punkte: {score}\n")
    frame.append("#" * (WIDTH + 2) + "\n")

    for y in range(HEIGHT):
        row = ["#"]
        for x in range(WIDTH):
            if (x, y) == snake[0]:
                row.append("@")
            elif (x, y) in snake[1:]:
                row.append("o")
            elif (x, y) in apples:
                row.append("O")
            else:
                row.append(" ")
        row.append("#\n")
        frame.append("".join(row))

    frame.append("#" * (WIDTH + 2) + "\n")
    frame.append("\nSteuerung: W/A/S/D | Q = Beenden\n")

    print("".join(frame), end="", flush=True)


def spawn_apple(snake, apples):
    while True:
        new_apple = (random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1))
        if new_apple not in snake and new_apple not in apples:
            return new_apple


def main():
    snake = [(WIDTH // 2, HEIGHT // 2)]
    direction = (1, 0)
    apples = [spawn_apple(snake, []) for _ in range(5)]
    score = 0
    base_speed = 0.1
    print("\033[2J\033[?25l", end="")

    old_settings = init_linux()

    try:
        while True:
            draw(snake, apples, score)

            key = get_key()
            if key == "w" and direction != (0, 1):
                direction = (0, -1)
            elif key == "s" and direction != (0, -1):
                direction = (0, 1)
            elif key == "a" and direction != (1, 0):
                direction = (-1, 0)
            elif key == "d" and direction != (-1, 0):
                direction = (1, 0)
            elif key == "q":
                break

            new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

            if (
                new_head[0] < 0
                or new_head[0] >= WIDTH
                or new_head[1] < 0
                or new_head[1] >= HEIGHT
                or new_head in snake
            ):
                print("\033[?25h", end="")
                print("\nGAME OVER")
                print(f"Endpunktzahl: {score}")
                break

            snake.insert(0, new_head)

            if new_head in apples:
                apples.remove(new_head)
                score += 1
                apples.append(spawn_apple(snake, apples))
                base_speed = max(0.07, base_speed - 0.003)
            else:
                snake.pop()

            if direction in [(0, 1), (0, -1)]:
                time.sleep(base_speed * 1.5)
            else:
                time.sleep(base_speed)

    finally:
        reset_linux(old_settings)
        print("\033[?25h", end="")


if __name__ == "__main__":
    main()
