from file import HistoryController

historyController = HistoryController('../history.json')

history = historyController.get()
print(history)
print(history['1'])
historyController.update(1, {'newest_flag': "yes"})
history = historyController.get()
print(history)
historyController.save()