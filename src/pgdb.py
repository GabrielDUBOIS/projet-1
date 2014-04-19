# -*- coding: Utf-8 -*-

### Importations des modules de la bibliotheque standard
import psycopg2 as pg  # @UnresolvedImport
import abc

### Déclaration des constantes de module
DB_NAME = 'hardview'
DB_USER = 'gabriel'
DB_PWD = 'XXXX'
DB_HOST = 'localhost'
DB_PORT = '5433'
DEFAULT_SCHEMA = 'public'
DEBUG = False

### Déclaration des classes


class DB:

    __slots__ = ['_connectStr', '_connection', '_cursor', ]

    def __init__(self):
        self.__release()
        if DEBUG:
            print('Initialisation de la classe %s' % self.__class__.__name__)

    def __release(self):
        self._connectStr = None
        self._connection = None
        self._cursor = None

    ## Méthodes d'instances
    def close_connection(self):
        self.cursor.close()
        self.connection.close()

    ## Propriétés / Fonctions décorées
    @property
    def connectStr(self):
        if not self._connectStr:
            self._connectStr = \
            'dbname={0} user={1} password={2} host={3} port={4}'. \
            format(DB_NAME, DB_USER, DB_PWD, DB_HOST, DB_PORT)
        return self._connectStr

    @property
    def connection(self):
        if not self._connection:
            self._connection = pg.connect(self.connectStr)
        return self._connection

    @connection.setter
    def connection(self, connection):
        if type(connection) == pg._psycopg.connection:
            self._connection = connection
        else:
            raise TypeError('Erreur de tye : type %s fourni en argument'
                            % type(connection))

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.connection.cursor()
        return self._cursor

    @cursor.setter
    def cursor(self, cursor):
        if type(cursor) == pg._psycopg.cursor:
            self._cursor = cursor
        else:
            raise TypeError('Erreur de type : type %s fourni en argument'
                            % type(cursor))


class HardView(DB):

    __slots__ = ['vmProperties', '_schema', '_tablesRecords', '_tablesObjects']

    _class_assoc = {}  # Foward prototypage completion

    def __init__(self, vmProperties=None):
        DB.__init__(self)
        if DEBUG:
            print('Initialisation de la classe %s' % self.__class__.__name__)
        self.vmProperties = vmProperties
        self.__release()

    def __release(self):
        self._tablesObjects = {}
        self._tablesRecords = {}
        self.schema = 'public'

    ## Méthodes d'instances
    def recieve_data(self, vmProperties):
        """Réception, découpage et distribution des données."""
        if DEBUG:
            print('Réception des données par la classe %s' %
            self.__class__.__name__)
        for aTable in self._class_assoc.keys():
            if not aTable == 'order':
                oTable = self._tablesObjects[aTable]
                if DEBUG:
                    print('Distribution des données pour la classe %s' % \
                    oTable.__class__.__name__)
                if aTable == 'tb_hosts':
                    properties = vmProperties
                elif aTable == 'tb_devs':
                    properties = oTable.get_dict_properties(vmProperties)

                if properties:
                    self._tablesRecords[aTable] = \
                    oTable.recieve_data(properties)

    def insert_data(self, withCommit=True):
        """Insertion des données dans chacune des tables déclarées."""
        for aTable in self._class_assoc['order']:
            if self._tablesRecords[aTable]:
                if DEBUG:
                    print('Insertion des données dans la table %s' % aTable)
                self._tablesObjects[aTable].insert_data(withCommit)

    def get_table_byname(self, aTable):
        """Retourne un objet table."""
        if aTable in self._tablesObjects.keys():
            oTable = self._tablesObjects[aTable]
        else:
            oTable = None
        return oTable

    def get_table_name_list(self):
        return list(self._tablesObjects.keys())

    def get_table_records_byname(self, aTable):
        if aTable in self._tablesRecords.keys():
            records = self._tablesRecords[aTable]
        else:
            records = ()
        return records

    def get_class_bytablename(self, aTable):
        oTable = self.get_table_byname(aTable)
        if oTable:
            cTable = oTable.__class__
        else:
            cTable = None
        return cTable

    ## Propriétés / Fonctions décorées

    @property
    def schema(self):
        if not self._schema:
            self._schema = DEFAULT_SCHEMA
        return self._schema

    @schema.setter
    def schema(self, arg):
        """Initialisation en cascade des variables d'instance schema pour
        toutes les tables déclarées."""
        self._schema = arg
        for aTable, cTable in self._class_assoc.items():
            if not aTable == 'order':
                oTable = cTable()
                if DEBUG:
                    print('Ajout du couple {%s:%s}'
                    ' au dictionnaire _tablesObjects' % (aTable, str(oTable)))
                oTable.schema = arg
                if DEBUG:
                    print('Nom du schema %s' % oTable.schema)
                self._tablesObjects[aTable] = oTable


class Table(metaclass=abc.ABCMeta):

    __slots__ = ['records', '_fields', '_fieldsAssoc', '_schema', '_strSql',
                 '_dbManager', '_cursor', '_connection']
    __slots__ = ['records', '_fields', '_fieldsAssoc', '_schema', '_strSql']
    fieldsName = ()
    fieldsType = ()
    _injected_references = ()
    """
    _dbManager = None
    _cursor = None
    _connection = None
    """
    def __init__(self, dbManager=None):
        if DEBUG:
            print('Initialisation de la classe %s' % self.__class__.__name__)
        self.dbManager = dbManager
        self.__release()

    def __release(self):
        self.records = ()  # stockage des records ((a,b,c,d),...)
        self._fields = {}
        self._fieldsAssoc = {}
        # self.schema = 'public'
        self._strSql = ''
        self._cursor = None
        self._connection = None

    ## Méthodes d'instance
    def recieve_data(self, data):
        """Réception et stockage des données dans la variable 'records'."""
        if DEBUG:
            print('Réception des données par la classe %s' %
            self.__class__.__name__)
        self.records = ()
        for record in data:
            if DEBUG:
                print('Ajout pour la table %s de l\'enregistrement %s ' %
                (self.name, record))
            values = ()
            for field in self.fieldsName:
                fType = self.fields[field]
                fieldValue = record[self.fieldsAssoc[field]]
                if type(fieldValue) == fType:
                    """
                    # Non implémentée actuellement
                    if field in self._injected_references:
                        self._injected_references[field] += (fieldValue,)
                    """
                    values += (fieldValue,)
                else:
                    raise TypeError('Erreur de type :\n'
                                    'champs %s de type %s\n'
                                    'valeur fournie %s de type %s' %
                                    (field, fType, fieldValue,
                                    type(fieldValue)))
            self.records += (values,)
        return self.records

    def insert_data(self, withCommit=True):
        if DEBUG:
            print('Shema %s. Exécution de l\'instruction SQL : %s' % \
            (self.schema, self.sqlInsertInstruction))
        self.cursor.execute(self.sqlInsertInstruction)
        if withCommit:
            self.connection.commit()
        self.sqlInsertInstruction = ''

    def close_connection(self):
        self._cursor = None
        self._connection = None
        self.cursor.close()
        self.connection.close()

    def delete_all_records_table(self, withCommit=False):
        sqlStr = 'DELETE FROM {0}.{1};'.format(self.schema, self.name)
        self.cursor.execute(sqlStr)
        if withCommit:
            self.connection.commit()

    ## Propriétés / Fonctions décoreés

    @property
    def schema(self):
        if not self._schema:
            self._schema = DEFAULT_SCHEMA
        return self._schema

    @schema.setter
    def schema(self, arg):
        self._schema = arg

    @property
    def dbManager(self):
        if not self._dbManager:
            self._dbManager = DB()
        return self._dbManager

    @dbManager.setter
    def dbManager(self, dbManager):
        self._dbManager = dbManager

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = self.dbManager.cursor
        return self._cursor

    @cursor.setter
    def cursor(self, arg):
        pass

    @property
    def connection(self):
        if not self._connection:
            self._connection = self.dbManager.connection
        return self._connection

    @connection.setter
    def connection(self, arg):
        self._connection = arg

    @property
    def fields(self):
        if not self._fields:
            self._fields = dict(zip(self.fieldsName, self.fieldsType))
        return self._fields

    @fields.setter
    def fields(self, arg):
        pass

    @property
    def fieldsAssoc(self):
        if not self._fieldsAssoc:
            self._fieldsAssoc = dict(zip(self.fieldsName, self.vPropsName))
        return self._fieldsAssoc

    @fieldsAssoc.setter
    def fieldsAssoc(self, arg):
        pass

    @property
    def sqlInsertInstruction(self):
        if not self._strSql:
            strValues = str(self.records)[1:-1]
            strFields = str(self.fieldsName). \
            replace('\'', '')
            self._strSql = "INSERT INTO {0}.{1} {2} VALUES {3};". \
            format(self.schema, self.name, strFields, strValues)
        return self._strSql

    @sqlInsertInstruction.setter
    def sqlInsertInstruction(self, strSql):
        self._strSql = strSql


class TbHosts(Table):

    name = 'tb_hosts'

    fieldsName = ('os', 'mor', 'hostname', 'name', 'cpu', 'memory')
    vPropsName = ('guest_id', 'mor', 'hostname', 'name', 'cpu', 'memory_mb')
    fieldsType = (str, int, str, str, int, int)

    # _injected_references = {'mor':()}

    def __init__(self, dbManager=None):
        Table.__init__(self, dbManager)


class TbDevs(Table):

    name = 'tb_devs'

    fieldsName = ('label', 'total', 'committed', 'ref_mor')
    vPropsName = ('label', 'total', 'committed', 'mor')
    fieldsType = (str, int, int, int)

    # _injected_references = {}

    def __init__(self, dbManager=None):
        Table.__init__(self, dbManager)

    ## Méthodes d'instance
    def get_dict_properties(self, vmProperties):
        properties = ()
        for aVmProperties in vmProperties:
            propsName = tuple((self.fieldsAssoc[field] \
                                  for field in self.fieldsName))
            if 'disks' in aVmProperties.keys():
                data = aVmProperties['disks']
                for record in data:
                    record += (aVmProperties['mor'],)
                    properties += (dict(zip(propsName, record)),)

        return properties

### Déclaration / Peuplage par prototypage
HardView._class_assoc = \
    {'tb_hosts': TbHosts, 'tb_devs': TbDevs,
    'order': ('tb_hosts', 'tb_devs')}


if __name__ == '__main__':

    db = HardView()

    data = [{'guest_id': 'ubu64', 'mor': 45632, 'os': 'ubu',
            'name': 'titi', 'hostname': 'ubutiti', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu64', 'mor': 1254, 'os': 'ubu',
              'name': 'toto', 'hostname': 'ubutoto', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 2', 30971820, 5494087),
            ('Disque dur 3', 30971820, 5494087)]},
            {'guest_id': 'ubu64', 'mor': 5847, 'os': 'ubu',
            'name': 'tata', 'hostname': 'ubutata', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 2', 30971820, 5494087),
            ('Disque dur 5', 30971820, 5494087)]}]

    for arg in ('test', 'public'):
        db.schema = arg
        oTable = db.get_table_byname('tb_hosts')
        oTable.delete_all_records_table(True)

    for arg in ('test', 'public'):
        db.schema = arg
        db.recieve_data(data)
        db.insert_data()
    db.close_connection()
    """
    for arg in ('test', 'public'):
        db.schema=arg
        oTable = db.get_table_byname('tb_hosts')
        oTable.delete_all_records_table(True)
        oTable.connection.close()
    """
    print(db.get_table_name_list())
    print(db.get_table_records_byname('tb_hosts'))
