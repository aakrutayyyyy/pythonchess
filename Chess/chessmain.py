# Main driver file.

import pygame as p
from Chess import chessengine
import sys

WIDTH=HEIGHT=512
DIMENSION=8
SQ_SIZE=HEIGHT//DIMENSION
MAX_FPS=15
IMAGES={}

def loadImages():
    pieces=['wR','wQ','wp','wN','wK','wB','bR','bQ','bp','bN','bK','bB']
    for piece in pieces:
        IMAGES[piece]=p.transform.scale(p.image.load("chess/"+piece+".png"),(SQ_SIZE,SQ_SIZE))

def main():
    p.init()
    screen=p.display.set_mode((WIDTH,HEIGHT))
    clock=p.time.Clock()
    screen.fill(p.Color("white"))
    gs=chessengine.GameState()
    loadImages()
    running=True
    sqSelected=()
    playerClicks=[]
    validMoves=gs.getValidMoves()
    moveMade=False
    gameOver=False
    animate=False
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running=False
            elif e.type==p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location=p.mouse.get_pos()
                    col=location[0]//SQ_SIZE
                    row=location[1]//SQ_SIZE
                    if sqSelected==(row,col):
                        sqSelected=()
                        playerClicks=[]
                    else:
                        sqSelected=(row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks)==2:
                        move=chessengine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move==validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade=True
                                animate=True
                                sqSelected=()
                                playerClicks=[]
                        if not moveMade:
                            playerClicks=[sqSelected]
            elif e.type==p.KEYDOWN:
                if e.key==p.K_z:
                    gs.undoMove()
                    moveMade=True
                    animate=False
                if e.key==p.K_r:
                    gs=chessengine.GameState()
                    validMoves=gs.getValidMoves()
                    sqSelected=()
                    playerClicks=[]
                    moveMade=False
                    animate=False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1],screen,gs.board,clock)
            validMoves=gs.getValidMoves()
            moveMade=False
            animate=False

        drawGameState(screen,gs,validMoves,sqSelected)
        if gs.checkMate:
            gameOver=True
            if gs.whiteToMove:
                drawText(screen,"BLACK WINS BY CHECKMATE")
            else:
                drawText(screen,"WHITE WINS BY CHECKMATE")
        elif gs.staleMate:
            gameOver=True
            drawText(screen,"STALEMATE")
        clock.tick(MAX_FPS)
        p.display.flip()

def highlightSquares(screen,gs,validMoves,sqSelected):
    if sqSelected!=():
        r,c=sqSelected
        if gs.board[r][c][0]== "w" if gs.whiteToMove else "b":
            s=p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('purple'))
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))
            s.fill(p.Color("red"))
            for move in validMoves:
                if move.startRow==r and move. startCol==c:
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))

def drawGameState(screen,gs,validMoves,sqSelected):
    drawBoard(screen)
    highlightSquares(screen,gs,validMoves,sqSelected)
    drawPieces(screen,gs.board)


def drawBoard(screen):
    global colors
    colors=[p.Color("white"),p.Color("grey")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
          color=colors[((r+c)%2)]
          p.draw.rect(screen,color,p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
     for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece=board[r][c]
            if piece!="--":
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def animateMove(move,screen,board,clock):
    global colors
    dr=move.endRow-move.startRow
    dc=move.endCol-move.startCol
    framepersq=10
    framecount=(abs(dr)+abs(dc))*framepersq
    for frame in range(framecount+1):
        r,c=(move.startRow + dr*frame/framecount,move.startCol + dc*frame/framecount)
        drawBoard(screen)
        drawPieces(screen,board)
        color=colors[(move.endRow+move.endCol)%2]
        endSquare=p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        if move.peiceCaptured!="--":
            screen.blit(IMAGES[move.peiceCaptured],endSquare)
        screen.blit(IMAGES[move.peiceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.flip()
        clock.tick(60)



def drawText(screen,text):
    font=p.font.SysFont("Helvitca",32,True,False)
    textObject=font.render(text,0,p.Color("Black"))
    textLocation=p.Rect(0,0,WIDTH,HEIGHT).move(WIDTH/2-textObject.get_width()/2,HEIGHT/2-textObject.get_height()/2)
    screen.blit(textObject,textLocation)
    textObject=font.render(text,0,p.Color('Black'))
    screen.blit(textObject,textLocation.move(2,2))

if __name__=="__main__":
 main()

