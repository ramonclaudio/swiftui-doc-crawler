# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import swiftui

if __name__ == "__main__":
    # Crawl all endpoints
    swiftui.crawl()