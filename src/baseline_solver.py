from env import Env


class BaselineSolver:
    
    def runStep(self, env: Env):
        
        if env.game_over:
            return False

        if env.first_move:
            env.first_move= False
            return True

        didWork =False

        while True:
            foundMove = False

            for row in range(env.rows ):
                for col in range(env.cols):
                    
                    if not env.revealed[row,col]:
                        continue

                    clueNum =int(env.adj_counts[row, col])
                    
                    if clueNum==0:
                        for dRow in (-1, 0, 1):
                        
                            for dCol in (-1,0, 1):
                                if dRow == 0 and dCol == 0:
                                    continue
                                nRow, nCol = row+dRow, col+dCol
                                if nRow < 0 or nRow >= env.rows or nCol < 0 or nCol >= env.cols:
                                    continue
                                if not env.revealed[nRow, nCol] and not env.flagged[nRow, nCol]:
                                    env.take_action (nRow, nCol,"reveal")
                                    foundMove = True
                                    if env.game_over:
                                        return True
                        continue

                    hiddenCells = []
                    flaggedCount= 0

                    for dRow in (-1,0, 1):
                        
                        for dCol in (-1,0, 1):
                            if dRow == 0 and dCol == 0:
                                continue
                            
                            nRow, nCol = row+dRow, col+dCol
                            
                            if nRow < 0 or nRow >= env.rows or nCol < 0 or nCol >= env.cols:
                                continue

                            if env.flagged[nRow, nCol]:
                                flaggedCount+= 1
                            elif not env.revealed [nRow, nCol]:
                                hiddenCells.append( (nRow,nCol))

                    minesLeft= clueNum- flaggedCount

                    if minesLeft > 0 and len( hiddenCells) ==minesLeft:
                        for hRow, hCol in hiddenCells:
                            
                            if not env.flagged [hRow, hCol]:
                                env.take_action(hRow,hCol,"flag" )
                                foundMove = True


                    elif minesLeft==0 and hiddenCells:
                        
                        for hRow, hCol in hiddenCells:
                            
                            if not env.revealed[hRow, hCol] and not env.flagged [hRow, hCol]:
                                env.take_action (hRow, hCol,"reveal" )
                                foundMove = True
                                
                                if env.game_over:
                                    return True

            if not foundMove:
                break

            didWork= True

        return didWork
