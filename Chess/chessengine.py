class GameState():
    def __init__(self):
        self.board=[
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bp","bp","bp","bp","bp","bp","bp","bp"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wp","wp","wp","wp","wp","wp","wp","wp"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        self.moveFunctions={'p':self.getPawnMoves,'R':self.getRookMoves,'N':self.getKnightMoves,
                            'B':self.getBishopMoves,'Q': self.getQueenMoves,'K': self.getKingMoves}
        self.whiteToMove=True
        self.moveLog=[]
        self.whiteKingLocation=(7,4)
        self.blackKingLocation=(0,4)
        self.checkMate=False
        self.staleMate=False
        self.enpassantPossible=()
        self.currentcastleRight=CastleRights(True,True,True,True)
        self.castleRightLog=[CastleRights(self.currentcastleRight.wks,self.currentcastleRight.bks,
                                          self.currentcastleRight.wqs,self.currentcastleRight.bqs)]


    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol]=move.peiceMoved
        self.moveLog.append(move)
        self.whiteToMove=not self.whiteToMove
        if move.peiceMoved=="wK":
            self.whiteKingLocation=(move.endRow,move.endCol)
        elif move.peiceMoved=="bK":
            self.blackKingLocation=(move.endRow,move.endCol)
        if move.isPawnPromotion:

            self.board[move.endRow][move.endCol]=move.peiceMoved[0]+"Q"
        if move.isenpassantMove:
            self.board[move.startRow][move.endCol]="--"
        if move.peiceMoved[1]=="p" and abs(move.startRow-move.endRow)==2:
            self.enpassantPossible=((move.startRow+move.endRow)//2,move.startCol)
        else:
            self.enpassantPossible=()

        if move.isCastleMove:
            if move.endCol-move.startCol==2:
                self.board[move.endRow][move.endCol-1]=self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1]="--"
            else:
                 self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-2]
                 self.board[move.endRow][move.endCol-2]="--"

        self.updatecastleRights(move)
        self.castleRightLog.append(CastleRights(self.currentcastleRight.wks,self.currentcastleRight.bks,
                                          self.currentcastleRight.wqs,self.currentcastleRight.bqs))

    def undoMove(self):
        if len(self.moveLog)!=0:
            move=self.moveLog.pop()
            self.board[move.startRow][move.startCol]=move.peiceMoved
            self.board[move.endRow][move.endCol]=move.peiceCaptured
            self.whiteToMove=not self.whiteToMove
            if move.peiceMoved=="wK":
                self.whiteKingLocation=(move.startRow,move.startCol)
            elif move.peiceMoved=="bK":
                self.blackKingLocation=(move.startRow,move.startCol)
            if move.isenpassantMove:
                self.board[move.endRow][move.endCol]="--"
                self.board[move.startRow][move.endCol]=move.peiceCaptured
                self.enpassantPossible=(move.endRow,move.endCol)
            if move.peiceMoved[1]=="p" and abs(move.startRow-move.endRow)==2:
                self.enpassantPossible=()
            self.castleRightLog.pop()
            newRights=self.castleRightLog[-1]
            self.currentcastleRight=CastleRights(newRights.wks,newRights.bks,newRights.wqs,newRights.bqs)
            if move.isCastleMove:
                if move.endCol-move.startCol==2:
                    self.board[move.endRow][move.endCol+1]=self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1]="--"
                else:
                     self.board[move.endRow][move.endCol-2]=self.board[move.endRow][move.endCol+1]
                     self.board[move.endRow][move.endCol+1]="--"
    def updatecastleRights(self,move):
        if move.peiceMoved=="wk":
            self.currentcastleRight.wks=False
            self.currentcastleRight.wqs=False
        elif move.peiceMoved=="bk":
            self.currentcastleRight.bks=False
            self.currentcastleRight.bqs=False
        elif move.peiceMoved=="wR":
            if move.startRow==7:
                if move.startCol==0:
                    self.currentcastleRight.wqs=False
                elif move.startCol==7:
                    self.currentcastleRight.wks=False
        elif move.peiceMoved=="bR":
            if move.startRow==0:
                if move.startCol==0:
                    self.currentcastleRight.bqs=False
                elif move.startCol==7:
                    self.currentcastleRight.bks=False







    def getValidMoves(self):
        tempenpassantPossible=self.enpassantPossible
        tempcastlemoves=CastleRights(self.currentcastleRight.wks,self.currentcastleRight.bks,
                                          self.currentcastleRight.wqs,self.currentcastleRight.bqs)

        moves=self.getAllPossibleMoves()
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.whiteToMove=not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove=not self.whiteToMove
            self.undoMove()
        if len(moves)==0:
            if self.inCheck():
                self.checkMate=True
            else:
                self.staleMate=True
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)
        self.enpassantPossible=tempenpassantPossible
        self.currentcastleRight=tempcastlemoves
        return moves

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0],self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0],self.blackKingLocation[1])


    def squareUnderAttack(self,r,c):
        self.whiteToMove=not self.whiteToMove
        oppMoves=self.getAllPossibleMoves()
        self.whiteToMove=not self.whiteToMove
        for move in oppMoves:
            if move.endRow==r and move.endCol==c:
                return True
        return False


    def getAllPossibleMoves(self):
        moves=[]
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn=self.board[r][c][0]
                if(turn=='w'and self.whiteToMove) or (turn=='b'and not self.whiteToMove):
                    piece=self.board[r][c][1]
                    self.moveFunctions[piece](r,c,moves)

        return moves

    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove:
            if self.board[r-1][c]=="--":
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="--":
                     moves.append(Move((r,c),(r-2,c),self.board))
            if c-1>=0:
                if self.board[r-1][c-1][0]=='b':
                    moves.append(Move((r,c),(r-1,c-1),self.board))
                elif (r-1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c-1),self.board,isenpassantMove=True))

            if c+1<=7:
                if self.board[r-1][c+1][0]=='b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r-1,c+1),self.board,isenpassantMove=True))

        else:
            if self.board[r+1][c]=="--":
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="--":
                     moves.append(Move((r,c),(r+2,c),self.board))
            if c-1>=0:
                if self.board[r+1][c-1][0]=='w':
                    moves.append(Move((r,c),(r+1,c-1),self.board))
                elif (r+1,c-1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c-1),self.board,isenpassantMove=True))

            if c+1<=7:
                if self.board[r+1][c+1][0]=='w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1,c+1)==self.enpassantPossible:
                    moves.append(Move((r,c),(r+1,c+1),self.board,isenpassantMove=True))


    def getRookMoves(self,r,c,moves):
        directions=((-1,0),(0,-1),(1,0),(0,1))
        enemy='b'if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemy:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self,r,c,moves):
        knightmoves=((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        ally="w" if self.whiteToMove else "b"
        for m in knightmoves:
            endRow=r+m[0]
            endCol=c+m[1]
            if 0<=endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=ally:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    def getBishopMoves(self,r,c,moves):
        directions=((-1,-1),(-1,1),(1,-1),(1,1))
        enemy='b'if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemy:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKingMoves(self,r,c,moves):
        Kmoves=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        ally="w" if self.whiteToMove else "b"
        for i in range (8):
            endRow=r+Kmoves[i][0]
            endCol=c+Kmoves[i][1]
            if 0<= endRow<8 and 0<=endCol<8:
                endPiece=self.board[endRow][endCol]
                if endPiece[0]!=ally:
                    moves.append(Move((r,c),(endRow,endCol),self.board))

    def getQueenMoves(self,r,c,moves):
        rdirections=((-1,0),(0,-1),(1,0),(0,1))
        enemy='b'if self.whiteToMove else 'w'
        for d in rdirections:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemy:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break
        directions=((-1,-1),(-1,1),(1,-1),(1,1))
        for d in directions:
            for i in range(1,8):
                endRow=r+d[0]*i
                endCol=c+d[1]*i
                if 0<=endRow<8 and 0<=endCol<8:
                    endPiece=self.board[endRow][endCol]
                    if endPiece=="--":
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                    elif endPiece[0]==enemy:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    else:
                        break
                else:
                    break

    def getCastleMoves(self,r,c,moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentcastleRight.wks) or (not self.whiteToMove and self.currentcastleRight.bks):
            self.getKingSideMoves(r,c,moves)
        if (self.whiteToMove and self.currentcastleRight.wqs) or (not self.whiteToMove and self.currentcastleRight.bqs):
            self.getQueenSideMoves(r,c,moves)

    def getKingSideMoves(self,r,c,moves):
        if self.board[r][c+1]=="--" and self.board[r][c+2]=="--" :
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2):
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))

    def getQueenSideMoves(self,r,c,moves):
         if (self.board[r][c-1]=="--" and self.board[r][c-2]=="--" and self.board[r][c-3]=='" --') :
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2):
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))


class CastleRights():
    def __init__(self,wks,wqs,bks,bqs):
        self.wks=wks
        self.wqs=wqs
        self.bks=bks
        self.bqs=bqs

class Move():

    ranksToRows={ "1":7,"2":6,"3": 5,"4":4,
                  "5":3,"6":2,"7":1,"8":0}
    rowsToRanks={v:k for k,v in ranksToRows.items()}
    filesToCols={ "a":0,"b":1,"c":2,"d":3,"e":4,
                  "f":5,"g":6,"h":7}
    colsToFiles={v:k for k,v in filesToCols.items()}
    def __init__(self,startSq,endSq,board,isenpassantMove=False,isCastleMove=False):
         self.startRow=startSq[0]
         self.startCol=startSq[1]
         self.endRow=endSq[0]
         self.endCol=endSq[1]
         self.peiceMoved=board[self.startRow][self.startCol]
         self.peiceCaptured=board[self.endRow][self.endCol]
         self.isPawnPromotion=(self.peiceMoved=="wp" and self.endRow==0) or (self.peiceMoved=="bp" and self.endRow==7)
         self.isenpassantMove=isenpassantMove
         if self.isenpassantMove:
             self.peiceCaptured="wp" if self.peiceMoved=="bp" else "bp"
         self.isCastleMove=isCastleMove
         self.moveId=self.startRow*1000+self.startCol*100+self.endRow*10+self.endCol

    def __eq__(self,other):
        if isinstance(other,Move):
            return self.moveId==other.moveId
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol)+self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c]+self.rowsToRanks[r]




