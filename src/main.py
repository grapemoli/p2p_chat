from client import *
import sys

def main ():
    app = QApplication (sys.argv)
    window = Client ()
    window.start ()
    window.show ()

    sys.exit (app.exec ())

if __name__ == "__main__":
    main ()
