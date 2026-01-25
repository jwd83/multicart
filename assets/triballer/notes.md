
## Tri-Baller game board dimensions:

  Playfield:
  - Width: 360px (15 columns × 24px bubble diameter)
  - Height: ~320px (from top at y=20 to shooter at y=340)
  - Left edge: 140px from screen left
  - Top edge: 20px from screen top

  Grid:
  - Columns: 15
  - Max rows: 20
  - Danger line: Row 16 (where game over triggers)

  Bubbles:
  - Radius: 12px
  - Diameter: 24px

  Screen:
  - Total resolution: 640×360 (the playfield is centered horizontally)

  Shooter position:
  - X: 320 (center)
  - Y: 340 (near bottom)

  The actual bubble play area is 360×384px if you count all 20 possible rows, but the visible/usable area before game over is 360×(16 rows × 24px) = 360×384px maximum, typically
  starting with fewer rows.