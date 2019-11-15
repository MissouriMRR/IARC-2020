import sys,os
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]
import unittest
from vision.interface import Environment
from vision.bounding_box import BoundingBox


class TestEnvironment(unittest.TestCase):

    def setUp(self):
        self.target = [
            BoundingBox(4, ","),
            BoundingBox(8, ","),
            BoundingBox(2, ","),
            BoundingBox(6, ","),
            BoundingBox(7, ","),
            BoundingBox(5, ',')
        ]

    def test_iter(self):
        env = Environment()
        env.bounding_boxes = self.target
        for i, bounding_boxes in enumerate(env):
            self.assertEqual(self.target[i % len(self.target)], bounding_boxes)
            if i > len(self.target) * 4:
                break
        else:
            self.fail()
        #values changing in tuple
        env.rects = (1, 2)
        iterator = iter(env)
        x = next(iterator)
        self.assertEqual(x, env.bounding_boxes[0])
        x = next(iterator)
        self.assertEqual(x, env.bounding_boxes[1])
        env.bounding_boxes = (7, 8, 9, 10)
        x = next(iterator)
        self.assertEqual(x, env.bounding_boxes[2])


    def test_update(self):
        env1 = Environment()
        env1.update(self.target)
        self.assertEqual(env1.bounding_boxes, self.target)


if __name__ == '__main__':
    unittest.main()
