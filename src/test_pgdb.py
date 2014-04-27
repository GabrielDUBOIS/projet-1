import psycopg2 as pg
import pgdb
import unittest


class TestDB(unittest.TestCase):

    def setUp(self):
        self.dbManager = pgdb.DB()
        self.connection = self.dbManager.connection
        self.cursor = self.dbManager.cursor

    def tearDown(self):
        self.cursor.close()
        self.connection.close()
        self.dbManager = None

    def test_connection(self):
        print('Test de la propriété DB.connection')
        self.assertEqual(type(self.connection),
                         pg._psycopg.connection,  # @UndefinedVariable
                         'Type d\'objet connection non attendu')

    def test_connection_setter(self):
        print('Affectation d\'une connection')
        self.dbManager.connection = self.connection
        self.connection = self.dbManager.connection
        self.assertEqual(type(self.connection),
                         pg._psycopg.connection,  # @UndefinedVariable
                         'Type d\'objet connection non attendu')

    def test_connection_setter_exception(self):
        print('Test de la gestion d\'exception sur la propriété DB.connection')
        with self.assertRaises(TypeError):
            self.dbManager.connection = None

    def test_cursor(self):
        print('Test de la propriété DB.cursor')
        self.assertEqual(type(self.cursor),
                         pg._psycopg.cursor,  # @UndefinedVariable
                         'Type d\'objet cursor non attendu')

    def test_cursor_setter(self):
        print('Affectation d\'un cursor')
        self.dbManager.cursor = self.cursor
        self.cursor = self.dbManager.cursor
        self.assertEqual(type(self.cursor),
                         pg._psycopg.cursor,  # @UndefinedVariable
                         'Type d\'objet cursor non attendu')

    def test_cursor_setter_exception(self):
        print('Test de la gestion d\'exception sur la propriété DB.cursor')
        with self.assertRaises(TypeError):
            self.dbManager.cursor = None


if __name__ == '__main__':
    unittest.main()
