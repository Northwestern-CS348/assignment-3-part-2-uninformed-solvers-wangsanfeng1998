
from solver import *
import queue



class SolverDFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        self.movables = queue.Queue()

    def get_children(self):
        movables = self.gm.getMovables()

        parent = self.currentState
        depth = parent.depth

        children = []


        for m in movables:
            self.gm.makeMove(m)
            s = self.gm.getGameState()


            game_state = GameState(s, depth + 1, m)
            game_state.parent = parent
            if game_state not in self.visited:
                children.append(game_state)
                self.visited[game_state] = False
            elif self.visited[game_state] == False:
                children.append(game_state)

            self.gm.reverseMove(m)


    
        return children


    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Depth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        ### Student code goes here
        #check for end condition
        if self.currentState.state == self.victoryCondition:
            return True
        self.visited[self.currentState] = True

        #get the state's children, as well as idenitfy the next child to visit
        next = self.currentState.nextChildToVisit
        self.currentState.children = self.get_children()

        #traverse each branch of the states through a loop
        while next == len(self.currentState.children):
            if self.currentState.depth == 0:
                next = self.currentState.nextChildToVisit
                break
            #store the move needed to reach the next state
            reverse = self.currentState.requiredMovable
            self.currentState = self.currentState.parent
            self.gm.reverseMove(reverse)
            next = self.currentState.nextChildToVisit
        
        #move on to the following child once one branch has been fully traversed
        next_state = self.currentState.children[next]

        if self.visited[next_state] == False:
            self.currentState.nextChildToVisit += 1
            self.gm.makeMove(next_state.requiredMovable)
            self.currentState = next_state
            return False
        
        if self.currentState.state == self.victoryCondition:
            return True
        return False

   

class SolverBFS(UninformedSolver):
    def __init__(self, gameMaster, victoryCondition):
        super().__init__(gameMaster, victoryCondition)
        self.nodes = queue.Queue()
        self.list_moves_root_to_child = dict()

    def get_children(self):
        movables = self.gm.getMovables()

        parent = self.currentState
        depth = parent.depth

        children = []

        for m in movables:
            self.gm.makeMove(m)
            s = self.gm.getGameState()

            parent_list_moves = []
            parent_list_moves = self.list_moves_root_to_child[parent].copy()

            game_state = GameState(s, depth + 1, m)
            game_state.parent = parent

            if game_state not in self.visited:
                children.append(game_state)
                self.visited[game_state] = False
                self.nodes.put(game_state)
                self.list_moves_root_to_child[game_state] = []
                self.list_moves_root_to_child[game_state].extend(parent_list_moves)
                self.list_moves_root_to_child[game_state].append(game_state)

            self.gm.reverseMove(m)

        return children

    

    def solveOneStep(self):
        """
        Go to the next state that has not been explored. If a
        game state leads to more than one unexplored game states,
        explore in the order implied by the GameMaster.getMovables()
        function.
        If all game states reachable from a parent state has been explored,
        the next explored state should conform to the specifications of
        the Breadth-First Search algorithm.

        Returns:
            True if the desired solution state is reached, False otherwise
        """
        ### Student code goes here
        if self.currentState.state == self.victoryCondition:
            return True

        self.visited[self.currentState] = True

        # inital state with root 
        if self.currentState.depth == 0:
            self.list_moves_root_to_child[self.currentState] = []

        # get the children of the current state 
        self.currentState.children = self.get_children()

        # get the list of moves that have already occurred by traveling from the current state to the root, then reversing the list
        old_moves = self.list_moves_root_to_child[self.currentState]
        old_moves.reverse()

        # reset the current state
        self.currentState = self.nodes.get()
        # get the moves that have to occur for the root to reach this new current state
        next_moves = self.list_moves_root_to_child[self.currentState]
        
        #travel to the root
        for old in old_moves:
            self.gm.reverseMove(old.requiredMovable)

        #travel from root to new current state
        for next in next_moves:
            self.gm.makeMove(next.requiredMovable)

        if self.currentState.state == self.victoryCondition:
            return True
        return False
        
        

