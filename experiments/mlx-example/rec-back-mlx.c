#include <mlx.h>
#include <unistd.h>

#define ROWS 15
#define COLS 15
#define CELL 40

#define WHITE  0xFFFFFF
#define BLACK  0x000000
#define GREEN  0x00CC66
#define RED    0xFF3333
#define BLUE   0x3399FF
#define GRAY   0xAAAAAA

typedef struct s_game
{
    void    *mlx;
    void    *win;
    int     maze[ROWS][COLS];
    int     state[ROWS][COLS];
}   t_game;

int maze[ROWS][COLS] = {
    {0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0},
    {1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 0},
    {0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0},
    {0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1},
    {0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1},
    {1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1},
    {0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0},
    {0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0},
    {0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
    {1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0},
    {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0}
};

void draw_cell(t_game *g, int r, int c, int color)
{
    int x;
    int y;

    y = r * CELL;
    while (y < (r + 1) * CELL - 1)
    {
        x = c * CELL;
        while (x < (c + 1) * CELL - 1)
        {
            mlx_pixel_put(g->mlx, g->win, x, y, color);
            x++;
        }
        y++;
    }
}

void draw_maze(t_game *g)
{
    int r;
    int c;
    int color;

    r = 0;
    while (r < ROWS)
    {
        c = 0;
        while (c < COLS)
        {
            if (g->maze[r][c] == 1)
                color = BLACK;
            else if (r == ROWS - 1 && c == COLS - 1)
                color = BLUE;
            else if (g->state[r][c] == 1)
                color = GREEN;
            else if (g->state[r][c] == 2)
                color = RED;
            else
                color = WHITE;

            draw_cell(g, r, c, color);
            c++;
        }
        r++;
    }
}

int solve(t_game *g, int r, int c)
{
    /* Reject out-of-bounds, walls, and visited cells */
    if (r < 0 || r >= ROWS || c < 0 || c >= COLS)
        return (0);
    if (g->maze[r][c] == 1 || g->state[r][c] != 0)
        return (0);

    /* Mark the current cell as part of the path */
    g->state[r][c] = 1;
    draw_maze(g);
    mlx_do_sync(g->mlx);
    usleep(100000);

    /* Exit reached */
    if (r == ROWS - 1 && c == COLS - 1)
        return (1);

    /* Try down, right, up, and left */
    if (solve(g, r + 1, c))
        return (1);
    if (solve(g, r, c + 1))
        return (1);
    if (solve(g, r - 1, c))
        return (1);
    if (solve(g, r, c - 1))
        return (1);

    /* Dead end: undo this choice */
    g->state[r][c] = 2;
    draw_maze(g);
    mlx_do_sync(g->mlx);
    usleep(80000);

    return (0);
}

int main(void)
{
    t_game g = {0};
    int r;
    int c;

    r = 0;
    while (r < ROWS)
    {
        c = 0;
        while (c < COLS)
        {
            g.maze[r][c] = maze[r][c];
            g.state[r][c] = 0;
            c++;
        }
        r++;
    }

    g.mlx = mlx_init();
    if (!g.mlx)
        return (1);

    g.win = mlx_new_window(
        g.mlx, COLS * CELL, ROWS * CELL, "Backtracking Maze"
    );
    if (!g.win)
        return (1);

    draw_maze(&g);
    solve(&g, 0, 0);

    /* Keep the final maze visible */
    mlx_loop(g.mlx);
    return (0);
}

/*
cc -Wall -Wextra -Werror rec-back-mlx.c \
  -I"$HOME/minilibx-linux" \
  -L"$HOME/minilibx-linux" \
  -lmlx -lXext -lX11 -lbsd -lm \
  -o mlx_test

./mlx_test
*/


/* MLX git repo - https://github.com/42Paris/minilibx-linux */