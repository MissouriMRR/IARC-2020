import timeit
import unittest
from ModuleInFrame import ModuleInFrame

path = 'D_Img3.jpg'
tests = 1

total = 0.0
print("Module is in frame:", ModuleInFrame(path))
total += timeit.timeit('ModuleInFrame(path)', setup='from __main__ import ModuleInFrame, path', number=tests)

print("Tests:", tests)
print("Total:", total, "seconds")
print("Average:", total / tests, "seconds")