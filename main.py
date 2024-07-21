from core import initialize


if __name__ == "__main__":
    systemStore = initialize()
    app = systemStore.get('app')
    app.run()
