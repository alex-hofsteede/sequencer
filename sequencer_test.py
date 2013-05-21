import sequencer
import unittest

class TestSequence(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_number_sequences(self):
        self.assertEqual(sequencer.recognise(['mon', 'tue', 'wed']), 'weekdays')
        self.assertEqual(sequencer.recognise([1,2,-3]), 'integers') #no pattern, should still recognise type
        self.assertEqual(sequencer.recognise([1.0,2.0,-3.0]), 'floats') #no pattern, should still recognise type
        #self.assertEqual(sequencer.recognise(['jan', 'february', 'mar']), 'months') #mixed types
        self.assertEqual(sequencer.recognise(['a','m','j','j']), 'months')
        self.assertEqual(sequencer.recognise(['m','t','w','t','f','m','t','w','t','f']), 'weekdays')
        self.assertEqual(sequencer.recognise(['boo','barf','derp']), None)
        self.assertEqual(sequencer.recognise(['23:45','23:50','23:55']), 'hour:min')
        self.assertEqual(sequencer.recognise(['23:45:01','23:50:02','23:55:03']), 'hour:min:sec')

    def test_detect_repeats(self):
        self.assertEqual(sequencer.detect_repeats([1,2,3,1,2,3,1,2,3,1,2,3]), [1,2,3]) #full repeated sequence
        self.assertEqual(sequencer.detect_repeats([2,4,6,2,5,6,2,4,6]), None) #sequence broken
        self.assertEqual(sequencer.detect_repeats([2,4,6,2,4,6,2,4]), [2,4,6]) #sequence not evenly divisible, has remainder
        self.assertEqual(sequencer.detect_repeats([2,4,6,2,4,6,2,5]), None) #sequence breaks in remainder portion
        self.assertEqual(sequencer.detect_repeats([5,5,3,5,5,5,5,3,5,5,5,5]), [5,5,3,5,5]) #repeated subsequences in main sequence

    def test_pattern(self):
        self.assertEqual(sequencer.pattern([1,2,3]), ([[1],[1.0]], sequencer.SEQ_ARITHMETIC ))
        self.assertEqual(sequencer.pattern([2,4,6,8]), ([[2],[2.0]], sequencer.SEQ_ARITHMETIC ))
        self.assertEqual(sequencer.pattern([1,2,3,1,2,3]), ([[1,2,3]], sequencer.SEQ_REPEATING ))
        self.assertEqual(sequencer.pattern([1,2,4,5,7,8]), ([[1],[1.0,2.0]], sequencer.SEQ_ARITHMETIC ))
        self.assertEqual(sequencer.pattern([1,2,4,8,16,32]), ([[1],[2.0]], sequencer.SEQ_GEOMETRIC )) #Detect geometric sequence with step 2
        self.assertEqual(sequencer.pattern([1,-2,4,-8,16,-32]), ([[1],[-2.0]], sequencer.SEQ_GEOMETRIC )) #Detect geometric sequence with negative step
        #self.assertEqual(sequencer.pattern([1,2,4,7,11]), ([[1],[1],[1.0]], sequencer.SEQ_ARITHMETIC )) #Detect increment in step length

    def test_extend(self):
        self.assertEqual(sequencer.extend(['N', 'O', 'F'], 3), ['Ne', 'Na', 'Mg']) #N,O,F could be months or elements, choose elements based on the better pattern match
        self.assertEqual(sequencer.extend([1,2,3], 3), [4,5,6])
        self.assertEqual(sequencer.extend(['M','T','W','T','F','S'], 3), ['S','M','T']) #test wrapping of pattern based on the match data, not the sequence itself. 
        self.assertEqual(sequencer.extend([1.2,1.4,1.6], 3), [1.8,2.0,2.2])
        self.assertEqual(sequencer.extend([1,2,4,5,7], 3), [8,10,11])
        self.assertEqual(sequencer.extend(['He', 'Li', 'Be'], 3), ['B', 'C', 'N'])
        self.assertEqual(sequencer.extend(['01:45','01:50','01:55'], 2), ['02:00','02:05'])
        self.assertEqual(sequencer.extend(['10:45','11:50','12:55'], 2), ['14:00','15:05'])
        self.assertEqual(sequencer.extend(['23:45','23:50','23:55'], 2), ['00:00','00:05'])
        self.assertEqual(sequencer.extend(['23:45:01','23:50:02','23:55:03'], 2), ['00:00:04','00:05:05'])

if __name__ == '__main__':
    unittest.main()
