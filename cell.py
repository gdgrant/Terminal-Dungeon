### Cell class for 2-D maze module
### Author:   gdgrant
### Date:     11/6/2018


class Cell:
    """ Unit cell for a square grid graph """

    def __init__(self, id, adj, acc):
        """ Set the cell's ID, adjacent cells, and accessible cells """
        self.id    = id     # Number of this cell
        self.adj   = adj    # List of ids of adjacent cells
        self.acc   = acc    # List of ids to which there is access

        # Check that all IDs used in initialization are valid
        self._validate_id(self.id, *self.adj, *self.acc)

        # Check that all accessible cells are adjacent
        self._validate_acc()


    def __repr__(self):
        """ Return the Cell's ID, adjacent cells, and accessible cells """
        return 'Cell(id={}, adj={}, acc={})'.format(self.id, self.adj, self.acc)


    def _validate_id(self, *ids):
        """ Check that all IDs are of the correct format """
        for i in ids:
            try:
                assert(type(i) == int)
            except AssertionError:
                raise Exception('Provided ID \'{}\' is invalid.'.format(i))


    def _validate_acc(self):
        """ Check that all accessible IDs are also adjacent """
        for i in self.acc:
            try:
                assert(i in self.adj)
            except AssertionError:
                raise Exception('Accessible ID \'{}\' is not adjacent.'.format(i))


    def can_access(self, target):
        """ Identify whether another cell is accessible """
        return 0 if target in self.acc else -1


    def block_access(self, target):
        """ Remove the target from list of accessible cells """
        if target in self.acc:
            self.acc.remove(target)
            return 0
        else:
            return -1

    def make_access(self, target):
        """ Add the target to list of accessible cells, if viable """
        if target in self.adj:
            if target not in self.acc:
                self.acc.append(target)
                return 0
            else:
                return -1
        else:
            return -2
