from game_master import GameMaster
from read import *
from util import *

class TowerOfHanoiGame(GameMaster):

    def __init__(self):
        super().__init__()
        
    def produceMovableQuery(self):
        """
        See overridden parent class method for more information.

        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?disk ?init ?target)')

    def getGameState(self):
        """
        Returns a representation of the game in the current state.
        The output should be a Tuple of three Tuples. Each inner tuple should
        represent a peg, and its content the disks on the peg. Disks
        should be represented by integers, with the smallest disk
        represented by 1, and the second smallest 2, etc.

        Within each inner Tuple, the integers should be sorted in ascending order,
        indicating the smallest disk stacked on top of the larger ones.

        For example, the output should adopt the following format:
        ((1,2,5),(),(3, 4))

        Returns:
            A Tuple of Tuples that represent the game state
        """
        ### Student code goes here
        facts = [0] * 3

        for i in range(0, 3):
            facts[i] = parse_input("fact: (on ?x peg" + str(i+1) + ")")

        bindings = [0] * 3

        pegs = [[],[],[]]

        for i in range(0, 3):
            bindings[i] = self.kb.kb_ask(facts[i])
        
        i = 0
        for b in bindings:
            if b != False:
                for binding in b.list_of_bindings:
                    curr_disk = binding[0].bindings[0].constant.element
                    if "disk" in curr_disk:
                        pegs[i].append(int(curr_disk[4:]))
                pegs[i].sort()
            i += 1

        game_state = (tuple(pegs[0]), tuple(pegs[1]), tuple(pegs[2]))
        return game_state

    def getFact(self, fact):
        """INTERNAL USE ONLY
        Get the fact in the KB that is the same as the fact argument
        Args:
            fact (Fact): Fact we're searching for
        Returns:
            Fact: matching fact
        """
        for kbfact in self.kb.facts:
            if fact == kbfact:
                return True
        return False


    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.

        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable disk1 peg1 peg3)

        Args:
            movable_statement: A Statement object that contains one of the currently viable moves

        Returns:
            None
        """
        ### Student code goes here
        if type(movable_statement) != Statement or not self.kb.kb_ask(Fact(movable_statement, [])):
            return None

        disk_name= movable_statement.terms[0].term.element
        current= movable_statement.terms[1].term.element
        target=movable_statement.terms[2].term.element

        #retract the facts and rules in the kb that involve disk_name being on top of the current peg
        old_fact = ["on", movable_statement.terms[0], movable_statement.terms[1]]
        old = Fact(Statement(old_fact), [])
        self.kb.kb_retract(old)

        new_top = parse_input("fact: (top " + disk_name + " " + current + ")")
        if self.kb.kb_ask(new_top):
            self.kb.kb_retract(new_top)

        # change the new top of the current peg
        prev_top_ask = parse_input("fact: (onTopOf " + str(disk_name) + " ?X)")
        if self.kb.kb_ask(prev_top_ask):
            for binding in self.kb.kb_ask(prev_top_ask):
                new_top = binding.bindings[0].constant
                # set the new top of the current peg
                self.kb.kb_assert(parse_input("fact: (top " +str(new_top) + " " + str(current) + ")"))
                # remove the ontop of fact
                self.kb.kb_remove(parse_input("fact: (onTopOf " + str(disk_name) + " " + str(new_top) + ")"))
        else:
            #ACCOUNT FOR CASE WHERE CURRENT PEG ONLY HAS A SINGLE DISK
            self.kb.kb_assert(parse_input("fact: (empty " + str(current) + ")"))

        #ACCOUNT FOR CASE WHERE TARGET PEG IS EMPTY,
        empty_bool = parse_input("fact: (empty " + str(target) + ")")
        if self.kb.kb_ask(empty_bool):
            self.kb.kb_retract(empty_bool)
        else:
            #get the old top of target
            old_top_fact = parse_input("fact: (top ?X " + str(target) + ")")
            old_top = self.kb.kb_ask(old_top_fact).list_of_bindings[0][0].bindings[0].constant.element
            #remove the fact that old_top is the top of the target peg
            self.kb.kb_retract(parse_input("fact: (top " + old_top + " " + str(target) + ")"))
            #add the facts that disk is now on top of the old_top
            self.kb.kb_add(parse_input("fact: (onTopOf " + str(disk_name) + " " + old_top + ")"))
        
        #add the facts that disk is now on top of current peg
        self.kb.kb_add(parse_input("fact: (top " + str(disk_name) + " " + str(target) + ")"))

        new_fact = ["on", movable_statement.terms[0], movable_statement.terms[2]]
        new = Fact(Statement(new_fact), [])
        self.kb.kb_assert(new)

      

    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.

        Args:
            movable_statement: A Statement object that contains one of the previously viable moves

        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[2], sl[1]]
        self.makeMove(Statement(newList))


class Puzzle8Game(GameMaster):

    def __init__(self):
        super().__init__()

    def produceMovableQuery(self):
        """
        Create the Fact object that could be used to query
        the KB of the presently available moves. This function
        is called once per game.
        Returns:
             A Fact object that could be used to query the currently available moves
        """
        return parse_input('fact: (movable ?piece ?initX ?initY ?targetX ?targetY)')

    def getGameState(self):
        """
        Returns a representation of the the game board in the current state.
        The output should be a Tuple of Three Tuples. Each inner tuple should
        represent a row of tiles on the board. Each tile should be represented
        with an integer; the empty space should be represented with -1.
        For example, the output should adopt the following format:
        ((1, 2, 3), (4, 5, 6), (7, 8, -1))
        Returns:
            A Tuple of Tuples that represent the game state
        """
        ### Student code goes here
        top_left = self.kb.kb_ask(parse_input("fact: (located ?X pos1 pos1)"))
        top_mid = self.kb.kb_ask(parse_input("fact: (located ?X pos2 pos1)"))
        top_right = self.kb.kb_ask(parse_input("fact: (located ?X pos3 pos1)"))
        mid_left = self.kb.kb_ask(parse_input("fact: (located ?X pos1 pos2)"))
        mid_mid = self.kb.kb_ask(parse_input("fact: (located ?X pos2 pos2)"))
        mid_right = self.kb.kb_ask(parse_input("fact: (located ?X pos3 pos2)"))
        bot_left = self.kb.kb_ask(parse_input("fact: (located ?X pos1 pos3)"))
        bot_mid = self.kb.kb_ask(parse_input("fact: (located ?X pos2 pos3)"))
        bot_right = self.kb.kb_ask(parse_input("fact: (located ?X pos3 pos3)"))

        row_1 = [top_left.list_of_bindings[0][0].bindings[0].constant.element, top_mid.list_of_bindings[0][0].bindings[0].constant.element, top_right.list_of_bindings[0][0].bindings[0].constant.element]
        row_2 = [mid_left.list_of_bindings[0][0].bindings[0].constant.element, mid_mid.list_of_bindings[0][0].bindings[0].constant.element, mid_right.list_of_bindings[0][0].bindings[0].constant.element]
        row_3 = [bot_left.list_of_bindings[0][0].bindings[0].constant.element, bot_mid.list_of_bindings[0][0].bindings[0].constant.element, bot_right.list_of_bindings[0][0].bindings[0].constant.element]

        for i in range(3):
            if row_1[i] == "empty":
                row_1[i] = -1
            else:
                row_1[i] = int(row_1[i][4:])

        for i in range(3):
            if row_2[i] == "empty":
                row_2[i] = -1
            else:
                row_2[i] = int(row_2[i][4:])

        for i in range(3):
            if row_3[i] == "empty":
                row_3[i] = -1
            else:
                row_3[i] = int(row_3[i][4:])

        gamestate = (tuple(row_1), tuple(row_2), tuple(row_3))
        return gamestate




    def makeMove(self, movable_statement):
        """
        Takes a MOVABLE statement and makes the corresponding move. This will
        result in a change of the game state, and therefore requires updating
        the KB in the Game Master.
        The statement should come directly from the result of the MOVABLE query
        issued to the KB, in the following format:
        (movable tile3 pos1 pos3 pos2 pos3)
        Args:
            movable_statement: A Statement object that contains one of the currently viable moves
        Returns:
            None
        """
        
        ### Student code goes here
        if type(movable_statement) != Statement or not self.kb.kb_ask(Fact(movable_statement, [])):
            return None

        tile_value = movable_statement.terms[0]
        curr_x = movable_statement.terms[1]
        curr_y = movable_statement.terms[2]
        target_x = movable_statement.terms[3]
        target_y = movable_statement.terms[4]

        old_list = ["located", tile_value, curr_x, curr_y]
        new_list = ["located", tile_value, target_x, target_y]

        old_fact = Fact(Statement(old_list), [])
        new_fact = Fact(Statement(new_list), [])

        old_empty = parse_input("fact: (located empty " + target_x.term.element + " " + target_y.term.element + ")")
        new_empty = parse_input("fact: (located empty " + curr_x.term.element + " " + curr_y.term.element + ")")

        self.kb.kb_retract(old_fact)
        self.kb.kb_assert(new_fact)
        self.kb.kb_retract(old_empty)
        self.kb.kb_assert(new_empty)



    def reverseMove(self, movable_statement):
        """
        See overridden parent class method for more information.
        Args:
            movable_statement: A Statement object that contains one of the previously viable moves
        Returns:
            None
        """
        pred = movable_statement.predicate
        sl = movable_statement.terms
        newList = [pred, sl[0], sl[3], sl[4], sl[1], sl[2]]
        self.makeMove(Statement(newList))