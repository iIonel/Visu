import sys
from .app import VisuApplication

def main():
    app = VisuApplication()
    return app.run(sys.argv)

if __name__ == "__main__":
    sys.exit(main())
