import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for var, words in self.domains.items():
            unmatched_words = set()
            for word in words:
                if len(word) != var.length:
                    unmatched_words.add(word)
            self.domains[var] = words - unmatched_words
        

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        ols = self.crossword.overlaps[x, y]
        # if there is no overlap
        if ols == None:
            return revised
        
        i, j = ols
        # set of possible words
        x_words = self.domains[x]
        y_words = self.domains[y]
        # if there is an overlap
        unmatched_words = set()
        for x_word in x_words:
            # if no possible word for x in y remove x_word from domain
            if all(x_word[i] != y_word[j] for y_word in y_words):
                unmatched_words.add(x_word)
                revised = True
        self.domains[x] = x_words - unmatched_words
        
        return revised

        



    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs == None:
            arcs = []
            for var in self.domains:
                neighbors = self.crossword.neighbors(var)
                for neighbor in neighbors:
                    arcs.append((var, neighbor))
        while len(arcs) != 0:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if len(self.domains[x]) == 0:
                    return False
                else: 
                    for neighbor in self.crossword.neighbors(x) - set([y]):
                        if (neighbor, x) not in arcs:
                            arcs.append((neighbor, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        
        for var in self.domains:
            if not var in assignment.keys():
                return False
            if not assignment[var]:
                return False
        
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(assignment) != 0:
            # check the length
            for var, value in assignment.items():
                if var.length != len(value):
                    print("where")
                    return False
            # check the neighbors
                neighbors = self.crossword.neighbors(var)
                if len(neighbors) == 0:
                    continue
                for neighbor in neighbors:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if neighbor in assignment:
                        if value[i] != assignment[neighbor][j]:
                            return False
                    else:
                        if all(value[i] != neighbor_value[j] for neighbor_value in self.domains[neighbor]):
                            return False
        
        if len(assignment) > 2:
            # Check for distinctness
            for key in assignment:
                for key2 in assignment:
                    if key == key2:
                        continue
                    if assignment[key] == assignment[key2]:
                        print("there")
                        return False
            # for i, v1 in enumerate(assignment.values()):
            #     if len(assignment) == i:
            #         break
            #     for v2 in list(assignment.values())[i + 1:]:
            #         print("v1:", v1, "v2:", v2)
            #         if v1 == v2:
            #             return False
        
        return True
        
        


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        unassigned = self.domains.copy()
        if len(assignment) > 0:
            for v_a in assignment:
                unassigned.pop(v_a)
        # Let's assume that var is not in assignment
        n_of_constraints = {}# least n first, value: number of constraints
        for value in unassigned[var]:
            for neighbor in self.crossword.neighbors(var):# get var's neighbor
                i, j = self.crossword.overlaps[var, neighbor]
                if neighbor in assignment:
                    n_of_constraints[value] = 0
                    continue
                for neighbor_value in unassigned[neighbor]:
                    if value[i] != neighbor_value[j]:
                        if value in n_of_constraints:
                            n_of_constraints[value] += 1
                        else:
                            n_of_constraints[value] = 1
                    else:
                        if value in n_of_constraints:
                            n_of_constraints[value] += 0
                        else:
                            n_of_constraints[value] = 0
        
        # print("n_of_constraints", n_of_constraints)
        # if len(n_of_constraints) == len(unassigned[var]):
        #     print("yes")
        #     print(len(n_of_constraints), n_of_constraints, len(unassigned[var]), unassigned[var])
        # else:
        #     print("no")
        #     print(len(n_of_constraints), n_of_constraints, len(unassigned[var]), unassigned[var])
        
        sorted_domain = sorted(list(unassigned[var]), key=lambda value: n_of_constraints[value])
        print("sorted_domain", sorted_domain)
        return sorted_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = {}# key: variable, value: set of values
        for var in self.crossword.variables:
            if not var in assignment.keys():
                unassigned[var] = self.domains[var]

        sorted_unassigned = sorted(unassigned.items(), key=lambda item: len(item[1]))
        ordered_vars = [i[0] for i in sorted_unassigned]
        
        # check for degrees
        has_same_remaining_values = []
        for i in range(len(ordered_vars)):
            if len(unassigned[ordered_vars[0]]) == len(unassigned[ordered_vars[i]]):
                has_same_remaining_values.append(ordered_vars[i])
        
        if has_same_remaining_values:
            return max(has_same_remaining_values, key=lambda var: len(self.crossword.neighbors(var)))
            
        return ordered_vars[0]
        

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            if self.consistent(assignment):
                assignment[var] = value
                result = self.backtrack(assignment)
                if result is not None:
                    return result
                assignment.pop(var)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
