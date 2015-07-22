# -*- coding: utf-8 -*-

DEBUG=False

def log(message):
    print message

def error(message):
    print "ERROR: {}".format(message)

def debug_mode(switch):
    global DEBUG
    DEBUG = switch

def debug(message):
    if DEBUG:
        print "DEBUG: {}".format(message)
