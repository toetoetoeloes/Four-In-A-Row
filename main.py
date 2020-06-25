# ********************************************************************************
#
#                                    FOUR IN A ROW
#
# HOW TO PLAY
#
#     Click with the left mouse button in a column to insert a disc or press a
#     number from 1 to 7. Click the right mouse button or press N to start a new
#     game.
#
#
# REMARKS
#
#     * If you change the constant COLS to something bigger than 7, you will not
#       be able to insert a disc in columns > 7 because the program checks if the
#       number pressed is in range 1-7.
#
#     * The player always plays with yellow.
# 
# ********************************************************************************

import random
import copy
import ctypes
import sys
import tkinter as tk
import tkinter.messagebox


# --------------------------------------------------------------------------------
# CONSTANTS
# --------------------------------------------------------------------------------

APPTITLE = "Four In A Row"

ROWS = 6
COLS = 7

GRIDPADDING = 10    # In pixels.
CELLSPACING = 1     # In pixels.

COMMAND_NEWGAME = 1
COMMAND_INSERTDISC = 2


# --------------------------------------------------------------------------------
# GLOBALS
# --------------------------------------------------------------------------------

MainWindow = None   # Tk root widget
Canvas = None       # Tk canvas widget

GridX = 0
GridY = 0

Grid = []
for i in range(ROWS):
    Grid.append([0] * COLS)

CellSize = 0        # Size of a gray box.

# Cells is a list of lists containing pairs of Tk rectangle tags and
# ellipse tags: [[[rectangle id, disc id], [rectangle id, disc id], ...]].
Cells = []

GameOver = False


# --------------------------------------------------------------------------------
# GRID
# --------------------------------------------------------------------------------

def GetDiscCount(grid):
    NumDiscs = 0
    for row in grid:
        for col in row:
            if col > 0:
                NumDiscs += 1
    return NumDiscs

# ------------------------------------------------------------------------------

def FindFirstEmptyCell(grid, col):
    row = len(grid) - 1
    while row >= 0:
        if grid[row][col] == 0:
            return row
        row -= 1
    return -1

# --------------------------------------------------------------------------------

def InsertDisc(grid, col, player):
    row = FindFirstEmptyCell(grid, col)
    if row >= 0:
        grid[row][col] = player
        return row
    return -1

# --------------------------------------------------------------------------------

def FourInARow(grid, player):
    for row in range(ROWS - 1, -1, -1):
        for col in range(COLS):
            # Check right.
            if col <= COLS - 4 and \
                grid[row][col] == player and \
                grid[row][col + 1] == player and \
                grid[row][col + 2] == player and \
                grid[row][col + 3] == player:
                return True
            # Check up.
            if row >= 3 and \
                grid[row][col] == player and \
                grid[row - 1][col] == player and \
                grid[row - 2][col] == player and \
                grid[row - 3][col] == player:
                return True
            # Check diagonally /.
            if row >= 3 and col <= COLS - 4 and \
                grid[row][col] == player and \
                grid[row - 1][col + 1] == player and \
                grid[row - 2][col + 2] == player and \
                grid[row - 3][col + 3] == player:
                return True
            # Check diagonally  \.
            if row <= ROWS - 4 and col <= COLS - 4 and \
                grid[row][col] == player and \
                grid[row + 1][col + 1] == player and \
                grid[row + 2][col + 2] == player and \
                grid[row + 3][col + 3] == player:
                return True
    return False


# --------------------------------------------------------------------------------
# ARTIFICIAL INTELLIGENCE
# --------------------------------------------------------------------------------

def NextBotMove(grid):
    if GetDiscCount(grid) < 5:
        return random.randint(0, COLS - 1)
    # Can we score?
    for col in range(COLS):
        grid_copy = copy.deepcopy(grid)
        InsertDisc(grid_copy, col, 2)
        if FourInARow(grid_copy, 2):
            return col
    # No, we cannot score. See if opponent can score and if so, block him.
    for col in range(COLS):
        grid_copy = copy.deepcopy(grid)
        InsertDisc(grid_copy, col, 1)
        if FourInARow(grid_copy, 1):
            return col
    # Create a list of cells where player 1 cannot score after our turn.
    cells = []
    for col in range(COLS):
        grid_copy = copy.deepcopy(grid)
        i = FindFirstEmptyCell(grid_copy, col)
        if i == 0:
            cells.append((i, col))
        elif i >= 1:
            # Don't insert a disc in this column if the other player
            # could score after our turn.
            grid_copy[i][col] = 2
            grid_copy[i - 1][col] = 1
            if not FourInARow(grid_copy, 1):
                # And don't insert a disc in this column if the other
                # player could block us if we could score the next time.
                # We must make sure [i][col] is not 2 because we would
                # always have four in a row if the two cells underneath
                # have the value 2, so we use 3 instead but we could also
                # use 0 or 1 for example.
                grid_copy[i][col] = 3
                grid_copy[i - 1][col] = 2
                if not FourInARow(grid_copy, 2):
                    cells.append((i, col))
    # Return one of those columns.
    if len(cells) > 0:
        # Create a list of cells with at least two neighboring '1' cells, horizontally or
        # vertically.
        cols = []
        for cell in cells:
            row, col = cell
            if ((col > 1 and grid[row][col - 1] == 1 and grid[row][col - 2] == 1) or \
                (col < COLS - 2 and grid[row][col + 1] == 1 and grid[row][col + 2] == 1)) or \
                (row < ROWS - 2 and grid[row + 1][col] == 1 and grid[row + 2][col] == 1):
                cols.append(col)
        if len(cols) > 0:
            return cols[random.randint(0, len(cols) - 1)]
        else:
            return cells[random.randint(0, len(cells) - 1)][1]
    else:
        # Choose a column at random.
        cols = []
        for col in range(COLS):
            if grid[0][col] == 0:
                cols.append(col)
        if len(cols) > 0:
            return cols[random.randint(0, len(cols) - 1)]
        else:
            return -1
    

# --------------------------------------------------------------------------------
# GAME
# --------------------------------------------------------------------------------
    
def DoCommand(command, *args):
    if command == COMMAND_NEWGAME:
        StartNewGame = True
        if not GameOver:
            if tk.messagebox.askyesno(APPTITLE, "Are you sure you want to start a new game?") != tk.YES:
                StartNewGame = False
        if StartNewGame:
            NewGame()
    elif command == COMMAND_INSERTDISC:
        col = args[0]
        player = args[1]
        row = InsertDisc(Grid, col, player)
        if row >= 0:
            if __debug__:
                print("{:>6} {:>6}".format(player, col))
            Grid[row][col] = player
            if player == 1:
                color = "yellow"
            else:
                color = "red"
            Cells[row][col][1] = Canvas.create_oval(0, 0, 10, 10, fill=color, width=0)
            OnResize(None)
            if FourInARow(Grid, player):
                EndGame(player)
            elif GetDiscCount(Grid) == ROWS * COLS:
                EndGame(-1)
            else:
                if player == 1:
                    MainWindow.after(1000 + random.randint(100, 1000), OnTimer)
            
# --------------------------------------------------------------------------------

def CreateGridView():
    for i in range(ROWS):
        row = []
        for j in range(COLS):
            cell = [Canvas.create_rectangle(0, 0, 0, 0, fill="black", width=0), None]
            if Grid[i][j] > 0:
                if Grid[i][j] == 1:
                    color = "yellow"
                else:
                    color = "red"
                cell[1] = Canvas.create_oval(0, 0, 0, 0, fill=color, width=0)
            row.append(cell)
        Cells.append(row)
    Canvas.bind("<Button-1>", OnGridViewLeftMouseClick)
    Canvas.bind("<Button-3>", OnGridViewRightMouseClick)
    Canvas.bind("<Key>", OnGridViewKeyPress)

# --------------------------------------------------------------------------------

def OnResize(event):
    global GridX, GridY, CellSize
    ClientWidth = Canvas.winfo_width()
    ClientHeight = Canvas.winfo_height()
    # Determine cell size.
    CellSize = (ClientHeight - ((ROWS + 1) * CELLSPACING) - GRIDPADDING * 2) // ROWS
    if COLS * (CellSize + CELLSPACING) + CELLSPACING + GRIDPADDING * 2 > ClientWidth:
        CellSize = (ClientWidth - ((COLS + 1) * CELLSPACING) - GRIDPADDING * 2) // COLS
    if CellSize < 0:
        CellSize = 0
    # Determine grid location.
    GridX = GRIDPADDING + (ClientWidth - (COLS * (CellSize + CELLSPACING) + CELLSPACING + GRIDPADDING * 2)) // 2
    GridY = GRIDPADDING + (ClientHeight - (ROWS * (CellSize + CELLSPACING) + CELLSPACING + GRIDPADDING * 2)) // 2
    # Determine location of rectangular cells and discs.
    y = GridY
    for i in range(ROWS):
        x = GridX
        for j in range(COLS):
            Canvas.coords(Cells[i][j][0], x, y, x + CellSize, y + CellSize)
            if Cells[i][j][1] != None:
                diff = int(round(CellSize * (1.0 - 0.8)) // 2)
                Canvas.coords(Cells[i][j][1], x + diff, y + diff, x + CellSize - diff, y + CellSize - diff)
            x += CellSize + CELLSPACING
        y += CellSize + CELLSPACING

# --------------------------------------------------------------------------------

def OnTimer():
    col = NextBotMove(Grid)
    if col == -1:
        EndGame(-1)
    else:
        DoCommand(COMMAND_INSERTDISC, col, 2)
    
# --------------------------------------------------------------------------------

def GetColumnAt(x, y):
    for i in range(COLS):
        cx = GridX + i * (CellSize + CELLSPACING)
        if x >= cx and x < cx + CellSize:
            return i
    return -1

# --------------------------------------------------------------------------------

def OnGridViewLeftMouseClick(event):
    if not GameOver:
        col = GetColumnAt(event.x, event.y)
        if col >= 0:
            DoCommand(COMMAND_INSERTDISC, col, 1)

# --------------------------------------------------------------------------------

def OnGridViewRightMouseClick(event):
    DoCommand(COMMAND_NEWGAME)
            
# --------------------------------------------------------------------------------

def OnGridViewKeyPress(event):
    if event.char.upper() == 'N':
        DoCommand(COMMAND_NEWGAME)
        return
    if not GameOver:
        if event.char in ('1', '2', '3', '4', '5', '6', '7'):
            col = int(event.char)
            if col >= 1 and col <= COLS:
                DoCommand(COMMAND_INSERTDISC, col - 1, 1)
    
# --------------------------------------------------------------------------------

def NewGame():
    global GameOver
    if __debug__:
        print("Player Column")
        print("------ ------")
    GameOver = False
    for row in range(ROWS):
        for col in range(COLS):
            Grid[row][col] = 0
            Canvas.delete(Cells[row][col][1])
    ActivePlayer = random.randint(1, 2)
    if ActivePlayer == 2:
        col = random.randint(0, COLS - 1)
        InsertDisc(Grid, col, 2)
        Cells[ROWS - 1][col][1] = Canvas.create_oval(0, 0, 10, 10, fill="red", width=0)
        ActivePlayer = 1
    OnResize(None)

# --------------------------------------------------------------------------------

def EndGame(winning_player):
    global GameOver
    if __debug__:
        print()
    GameOver = True
    if winning_player == 1:
        message = "YELLOW WINS !"
    elif winning_player == 2:
        message = "RED WINS !"
    else:
        message = "GAME OVER !"
    tk.messagebox.showinfo(APPTITLE, message, parent=MainWindow)
    if tk.messagebox.askyesno(APPTITLE, "Do you want to play again?") == tk.YES:
        NewGame()


# --------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------

if "win" in sys.platform:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

random.seed()

MainWindow = tk.Tk()
MainWindow.title(APPTITLE)
MainWindow.geometry("1024x768")
MainWindow.bind("<Configure>", OnResize)

Canvas = tk.Canvas(MainWindow, bg="gray20", bd="0", highlightthickness=0)
CreateGridView()
Canvas.pack(fill=tk.BOTH, expand=1)
Canvas.focus_set()

NewGame()

MainWindow.mainloop()

   

