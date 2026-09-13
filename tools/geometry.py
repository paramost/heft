"""The board's drawing constants, as index.html has them. Shared by generate.py, clearance.py
and select.py; kept apart so clearance.py can import them without importing the generator."""
import math

U, DROP, HOOKDROP, R_GLYPH = 22.0, 56.0, 30.0, 21.0
MAX_TILT = math.radians(15)
FLOOR_DEG, JND_DEG = 1.25, 1.25
STAGE_W, STAGE_H = 366.0, 405.0          # a 390x844 phone, 48svh stage
