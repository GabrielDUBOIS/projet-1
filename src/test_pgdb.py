import sys
import psycopg2 as pg
import pgdb
import unittest


def setUpModule():
    pass


def tearDownModule():
    pass


class A1DBTestCase(unittest.TestCase):

    dbManager = None
    connection = None
    cursor = None

    @classmethod
    def setUpClass(cls):
        cls.dbManager = pgdb.DB()
        cls.connection = cls.dbManager.connection
        cls.cursor = cls.dbManager.cursor

    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.connection.close()
        cls.dbManager = None

    def setUp(self):
        #print(self.id())
        pass

    def tearDown(self):
        pass

    def test_1A_connection(self):
        self.assertEqual(type(self.connection),
                         pg._psycopg.connection,  # @UndefinedVariable
                         'Type d\'objet connection non attendu')

    def test_1B_connection_setter(self):
        self.dbManager.connection = self.connection  # Affectation (@.setter)
        self.connection = self.dbManager.connection
        self.assertEqual(type(self.connection),
                         pg._psycopg.connection,  # @UndefinedVariable
                         'Type d\'objet connection non attendu')

    def test_1C_connection_setter_exception(self):
        with self.assertRaises(TypeError):
            self.dbManager.connection = None

    def test_1D_cursor(self):
        self.assertEqual(type(self.cursor),
                         pg._psycopg.cursor,  # @UndefinedVariable
                         'Type d\'objet cursor non attendu')

    def test_1E_cursor_setter(self):
        self.dbManager.cursor = self.cursor  # Affectation (@.setter)
        self.cursor = self.dbManager.cursor
        self.assertEqual(type(self.cursor),
                         pg._psycopg.cursor,  # @UndefinedVariable
                         'Type d\'objet cursor non attendu')

    def test_1F_cursor_setter_exception(self):
        with self.assertRaises(TypeError):
            self.dbManager.cursor = None


class A2HardViewTestCase(unittest.TestCase):

    dbManager = None
    connection = None
    cursor = None
    data = None

    @classmethod
    def setUpClass(cls):

        cls.dbManager = pgdb.HardView()
        cls.dbManager.schema = 'test'
        cls.connection = cls.dbManager.connection
        cls.cursor = cls.dbManager.cursor
        cls.data = \
            [{'guest_id': 'ubu64', 'mor': 45632, 'os': 'ubu',
            'name': 'tititi', 'hostname': 'ubutiti', 'cpu': 2,
            'memory_mb':1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu64', 'mor': 1254, 'os': 'ubu',
            'name': 'tototo', 'hostname': 'ubutoto', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 2', 30971820, 5494087),
            ('Disque dur 3', 30971820, 5494087)]},
            {'guest_id': 'ubu64', 'mor': 5847, 'os': 'ubu',
            'name': 'tata', 'hostname': 'ubutata', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 2', 30971820, 5494087),
            ('Disque dur 5', 30971820, 5494087)]},
            {'guest_id': 'ubu64', 'mor': 47732, 'os': 'ubu',
            'name': 'tutotu', 'hostname': 'ubututu', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu32', 'mor': 47799, 'os': 'ubu',
            'name': 'tutytu', 'hostname': 'ubutytu', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu64', 'mor': 472229, 'os': 'ubu',
            'name': 'tutrrrtu', 'hostname': 'ubuyotou', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'W732', 'mor': 411129, 'os': 'W7',
            'name': 'zszsezdeu', 'hostname': 'ezlfjezklje', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 1', 20971520, 8494080)]}]

        cls.vmValueTest = ('W732', 411129, 'ezlfjezklje', 'zszsezdeu', 2, 1024)
        cls.diskValueTest = ('Disque dur 1', 20971520, 8494080, 411129)
        cls.assocTest = {'tb_hosts': cls.vmValueTest,
                         'tb_devs': cls.diskValueTest}

    @classmethod
    def tearDownClass(cls):
        cls.cursor.close()
        cls.connection.close()
        cls.dbManager = None

    def setUp(self):
        #print(self.id())
        pass

    def tearDown(self):
        pass

    def test_1A_recieve_data(self):
        """Test de la réception des données."""
        self.dbManager.recieve_data(self.data)
        for tb, value in self.assocTest.items():
            with self.subTest(tb=tb):
                self.assertIn(value, self.dbManager._tablesRecords[tb])

    def test_1B_insert_data(self):
        self.dbManager.insert_data(True)

        for tb, value in self.assocTest.items():
            with self.subTest(tb=tb, value=value):
                strFields = \
                str(self.dbManager._tablesObjects[tb].fieldsName). \
                replace('\'', '')[1:-1]

                strSql = \
                "SELECT {0} FROM {1}.{2}". \
                format(strFields, self.dbManager.schema, tb)

                self.cursor.execute(strSql)
                self.assertIn(value, self.cursor.fetchall())

    def test_1C_get_table_byname(self):
        for tb in self.assocTest.keys():
            with self.subTest(tb=tb):
                self.assertIsInstance(self.dbManager.get_table_byname(tb),
                                      self.dbManager._class_assoc[tb])

    def test_1D_get_table_name_list(self):
        for tb in self.assocTest.keys():
            with self.subTest(tb=tb):
                self.assertIn(tb, self.dbManager.get_table_name_list())

    def test_1E_get_table_records_byname(self):
        for tb, value in self.assocTest.items():
            with self.subTest(tb=tb, value=value):
                self.assertIn(value,
                              self.dbManager.get_table_records_byname(tb))

    def test_1F_get_class_bytablename(self):
        for tb in self.assocTest.keys():
            with self.subTest(tb=tb):
                self.assertEqual(self.dbManager._class_assoc[tb],
                                 self.dbManager.get_class_bytablename(tb))

    @unittest.skip("Skip over the a test routine failed")
    def test_1G_fail(self):
        self.fail('Test d\'avortement de la routine de test')


@unittest.skip("Skip over the entire test routine")
class TableTestCase(unittest.TestCase):
    pass

testList = [A1DBTestCase, A2HardViewTestCase]
testLoad = unittest.TestLoader()

caseList = []
for testCase in testList:
    testSuite = testLoad.loadTestsFromTestCase(testCase)
    caseList.append(testSuite)

newSuite = unittest.TestSuite(caseList)

if __name__ == '__main__':
    """
    unittest.main()
    """
    testRunner = unittest.TextTestRunner(stream=sys.stderr, descriptions=True,
                                         verbosity=2)
    testResult = testRunner.run(newSuite)
    print("---- START OF TEST RESULTS\n")
    print(testResult)
    print("testResult::errors\n")
    print(testResult.errors)
    print("testResult::failures\n")
    print(testResult.failures)
    print("testResult::skipped\n")
    print(testResult.skipped)
    print("testResult::successful")
    print(testResult.wasSuccessful())
    print("testResult::test-run\n")
    print(testResult.testsRun)
    print("---- END OF TEST RESULTS\n")
