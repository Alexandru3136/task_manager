class SortStrategy:
    def sort(self, tasks):
        pass

class DateSortStrategy(SortStrategy):
    def sort(self, tasks):
        return sorted(tasks, key=lambda x: x.id)
