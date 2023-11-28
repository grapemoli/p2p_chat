import sys

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from requests import session
from client import *

client = Client()
client.start()