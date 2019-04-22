#!/usr/bin/env python3

import threading


class DBConnection(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def get_instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
                    print("connect to db")
        return cls.__singleton_instance


    def query(self):
        print("Make a query")


if __name__ == "__main__":
    conn = DBConnection.get_instance()
    conn.query()

    conn = DBConnection.get_instance()
    conn.query()
