# MLX Manual (plain-English companion to the man pages)

*This is a cheat sheet for `mlx_CLXV`, the Python-wrapped MinilibX library vendored
into `.mlx_build/mlx_CLXV/` by `make install`. The official man pages live at
`.mlx_build/mlx_CLXV/man/man3/*.3` — read with `man ./path/to/file.3`. This doc exists
because those pages describe the **C** API; this one describes what you actually call
from Python, grouped by what you're trying to do rather than alphabetically.*

Everything below is called as a method on an `Mlx` instance:

```python
from mlx import Mlx
m = Mlx()
mlx_ptr = m.mlx_init()
```

---

## 1. The lifecycle (call order matters)

```
mlx_init()                 ─┐  once, first thing
mlx_new_window()            │  once per window
                             │
  [optional: build an image, draw into it]
                             │
mlx_*_hook()  (any number)  │  register BEFORE mlx_loop(), or the
                             │  event can fire before anyone's listening
                             │
mlx_loop()                  ─┘  blocks forever; your hooks get called
                                 from inside here whenever their event fires
```

`mlx_loop()` never returns on its own. The only way out is a hook calling
`mlx_loop_exit()` — typically a key hook that checks "was this the Quit key?"

---

## 2. Every function, grouped by purpose

### Setup / teardown

| Call | Returns | What it does |
|---|---|---|
| `mlx_init()` | `mlx_ptr` | Starts the library. Must be first. Everything else needs this pointer. |
| `mlx_release(mlx_ptr)` | `0` on success | Frees everything tied to `mlx_ptr`. |

### Windows

| Call | Returns | What it does |
|---|---|---|
| `mlx_new_window(mlx_ptr, width, height, title)` | `win_ptr` | Opens a window. `(0,0)` is the **top-left** corner; x grows right, y grows **down**. |
| `mlx_clear_window(mlx_ptr, win_ptr)` | `0` on success | Wipes the window to black. |
| `mlx_destroy_window(mlx_ptr, win_ptr)` | `0` on success | Closes it. |

### Drawing — two different strategies

**Strategy A — one pixel at a time, straight to the window.** Simple, but one
Python→C call per pixel, so it's slow for anything bigger than a few dozen pixels.

| Call | Returns | What it does |
|---|---|---|
| `mlx_pixel_put(mlx_ptr, win_ptr, x, y, color)` | `0` on success | Sets one pixel directly on the live window. |

**Strategy B — build a whole frame off-screen, then blit it in one call.** This is
the one you want for redrawing an entire maze grid every time something changes.

| Call | Returns | What it does |
|---|---|---|
| `mlx_new_image(mlx_ptr, width, height)` | `img_ptr` | Allocates an off-screen pixel buffer. |
| `mlx_get_data_addr(img_ptr)` | `(pixels, bits_per_pixel, size_line, format)` | Gives you a writable `memoryview` into that buffer — this is what you actually write pixel bytes into. |
| `mlx_put_image_to_window(mlx_ptr, win_ptr, img_ptr, x, y)` | `0` on success | Blits the whole image onto the window at once, at position `(x, y)`. |
| `mlx_destroy_image(mlx_ptr, img_ptr)` | `0` on success | Frees it. |

> **Colour-format gotcha:** colours are packed 32-bit values, byte order
> `B8G8R8A8`. Depending on your machine's endianness that reads out as either
> `0xAARRGGBB` or `0xBBGGRRAA`. For images, `mlx_get_data_addr` tells you which
> (`format`: `0` = B8G8R8A8, `1` = A8R8G8B8) — don't assume, check it, or your wall
> colours will come out scrambled.

### Text / image-file convenience

| Call | Returns | What it does |
|---|---|---|
| `mlx_string_put(mlx_ptr, win_ptr, x, y, color, string)` | `0` on success | Draws text using MLX's built-in bitmap font. Good enough for your menu bar text. |
| `mlx_xpm_file_to_image(mlx_ptr, filename)` | `(img_ptr, width, height)` | Loads a `.xpm` file as an image. |
| `mlx_png_file_to_image(mlx_ptr, filename)` | `(img_ptr, width, height)` | Loads a `.png` file as an image. |

### The event loop and hooks

| Call | Returns | What it does |
|---|---|---|
| `mlx_loop(mlx_ptr)` | — (blocks) | Runs forever, dispatching to whatever hooks you registered. |
| `mlx_loop_exit(mlx_ptr)` | — | Call this *from inside a hook* to make `mlx_loop` return. This is your "Quit". |
| `mlx_key_hook(win_ptr, callback, param)` | `0` on success | `callback(keysym, param)` fires on **key release** (not press). |
| `mlx_mouse_hook(win_ptr, callback, param)` | `0` on success | `callback(button, x, y, param)` fires on a mouse click. |
| `mlx_expose_hook(win_ptr, callback, param)` | `0` on success | `callback(param)` fires when the window needs redrawing (e.g. after being uncovered). With modern X servers this often only fires once, at launch — don't rely on it for your main redraw logic. |
| `mlx_loop_hook(mlx_ptr, callback, param)` | `0` on success | `callback(param)` fires once per loop tick, continuously — your "idle"/animation hook. |
| `mlx_hook(win_ptr, x_event, x_mask, callback, param)` | `0` on success | Generic/raw version of the above three, keyed by X11 event numbers instead of a named hook. You won't need this unless the named hooks don't cover something. |

Pass `callback=None` to any `*_hook` call to unregister it.

> **Key hook detail:** `keysym` is an **X11 keysym**, not a raw scancode. Printable
> keys match their ASCII value (`'q'` → `113`, `'1'`–`'4'` → `49`–`52`), but special
> keys don't: **Escape is `65307`**, arrow keys are in the `65360s`. If you want to
> quit on Escape, check `if keysym == 65307`.

> **Ctrl-C note (already bit you once):** while `mlx_loop()` is running, Python can't
> catch `Ctrl-C` — control is inside the C library's own blocking loop. If you ever
> need to force-kill a hung test without hooks wired up yet, use `Ctrl-\` instead, or
> just `kill` the terminal.

### Mouse / misc extras

| Call | Returns | What it does |
|---|---|---|
| `mlx_mouse_hide(mlx_ptr)` / `mlx_mouse_show(mlx_ptr)` | `0` on success | Toggle cursor visibility. |
| `mlx_mouse_move(win_ptr, x, y)` | `0` on success | Warps the cursor to a position. |
| `mlx_mouse_get_pos(win_ptr)` | `(status, x, y)` | Current cursor position. |
| `mlx_do_key_autorepeatoff(mlx_ptr)` / `...on(mlx_ptr)` | `0` on success | Disable/enable OS key auto-repeat (handy so holding a key doesn't spam your key hook). |
| `mlx_get_screen_size(mlx_ptr)` | `(status, width, height)` | Monitor resolution. |

### Flush / sync (rarely needed directly — `mlx_loop` already flushes)

| Call | Returns | What it does |
|---|---|---|
| `mlx_do_sync(mlx_ptr)` | `0` on success | Waits until all pending draw requests for every window are actually sent/completed. |
| `mlx_sync(mlx_ptr, cmd, img_or_win_ptr)` | `0` on success | Same idea, targeted at one image/window. `cmd` is one of `Mlx.SYNC_IMAGE_WRITABLE`, `Mlx.SYNC_WIN_FLUSH`, `Mlx.SYNC_WIN_COMPLETED`. |

---

## 3. Finding more detail yourself

- **Man pages** (authoritative, C-level signatures): `man ./.mlx_build/mlx_CLXV/man/man3/<name>.3`
- **The exact Python signatures and docstrings** (what actually runs): `.mlx_build/mlx_CLXV/python/src/mlx/mlx.py` — every method here has a one-line docstring and full type hints; grep it directly if this table is ever out of date with the vendored version.
- **`mlx.h`** (the underlying C contract, with the author's own commentary on backend differences, macOS/Linux quirks, etc.): `.mlx_build/mlx_CLXV/src/mlx.h`

If a function here ever stops matching what's actually installed (e.g. after `make install` pulls a newer `mlx_CLXV` tag), trust `mlx.py` over this file.
