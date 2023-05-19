class Table:
    content: list
    curr_row: int
    horiz_header: list
    vert_header: list

    def __init__(self, horiz_head=None, vert_head=None):
        self.content = []
        self.curr_col = 0
        self.curr_row = 0
        self.horiz_header = horiz_head
        self.vert_header = vert_head

    def set_row_count(self, count: int):
        while len(self.content) < count:
            self.content.append([])

    def append_row(self, row: list):
        if self.curr_row < len(self.content):
            self.content[self.curr_row] = row
        else:
            self.content.append(row)
        self.curr_row += 1

    def append_col(self, col: list):
        self.set_row_count(len(col))
        for i in range(len(col)):
            self.content[i].append(col[i])

    def get_content(self):
        res = []
        if self.horiz_header is not None:
            res.append(self.horiz_header)
        for i, row in enumerate(self.content):
            if self.vert_header is not None:
                res.append([self.vert_header[i]] + row)
            else:
                res.append(row)
        return res

