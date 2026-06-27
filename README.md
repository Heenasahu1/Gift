# A Gift For You 🎁

A guarded digital birthday-gift web app built with Streamlit.

## How to run

1. Make sure you have Python 3.9+ installed.
2. Open a terminal in this folder.
3. Install the requirements:

   pip install -r requirements.txt

4. Run the app:

   streamlit run app.py

5. It opens automatically in your browser. Keep the `assets/` folder
   next to `app.py` — the app reads wallpaper.webp, Name.txt,
   Question.xlsx, puzzle.jpeg, message.txt, and gift.pdf from there.

## How it works

- **Landing page** — name is checked (case-insensitive) against the
  list in `assets/Name.txt`.
- **Are You Ready?** — confirmation screen before the quiz starts.
- **Quiz** — questions come from `assets/Question.xlsx`. Any of the
  "Answer 1..5" columns for a row count as correct (case-insensitive,
  exact match). Get 6 correct to finish.
  - Correct answers permanently remove that question and reveal one
    tile of the hidden photo (blurred grid-tile effect).
  - Wrong answers stay in the pool and can come back later.
  - A random funny/sweet message shows after every answer.
- **Reveal** — once all 6 tiles are unlocked, the full photo
  (`assets/puzzle.jpeg`) and a personalized note from
  `assets/message.txt` are shown (use `{name}` inside that file to
  auto-insert the verified name).
- **Gift** — `assets/gift.pdf` opens inline in the browser's PDF
  viewer with the toolbar hidden. There is no download button added
  by the app itself, though most browsers still let a user manually
  save any PDF they can view (Ctrl+S, browser menu, etc.) — that's a
  browser-level capability the app can't fully remove.

## Customizing

- Want a different reveal grid? Change `GRID_COLS` / `GRID_ROWS` at
  the top of `app.py` (must multiply to 6 to match "6 correct
  answers," or change both the grid size and the required correct
  count together).
- Want different jokes? Edit `CORRECT_MESSAGES` / `WRONG_MESSAGES`
  lists in `app.py`.
