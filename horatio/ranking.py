

class Ranking:
    ''' Builds a top-<length> ranking of <item> according to <value> '''

    def __init__(self, length):
        self.length = length
        self.items = list()
        self.min_value = -1

    def add(self, item, value):
        ''' adds to the ranking if item belongs, discards otherwise '''

        # discard unless ranking not complete or value below threshold
        if not (len(self.items) < self.length or value > self.min_value):
            return

        # append and sort
        self.items.append(tuple([item, value]))
        self.items.sort(key=lambda x: x[1], reverse=True)

        # cut out eventual item out of the ranking
        self.items = self.items[:self.length]

        # update entry barrier
        self.min_value = self.items[-1][1]

    def get(self):
        return self.items
