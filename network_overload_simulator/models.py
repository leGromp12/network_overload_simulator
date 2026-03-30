class packet():
    def __init__(self, id, arrival_time):
        self.id = id
        self.arrival_time = arrival_time

    def __repr__(self):
        return f"packet(id={self.id}, arrival_time={self.arrival_time})"
        