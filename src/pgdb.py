# -*- coding: Utf-8 -*-

### Importations des modules de la bibliotheque standard
import psycopg2 as pg
import abc

### Déclaration des constantes de module
DB_NAME = 'db_dev'
DB_USER = 'god'
DB_PWD = 'azerty123'
DB_HOST = '192.168.0.16'
DB_PORT = '5432'
DEFAULT_SCHEMA = 'public'
DEBUG = False

### Déclaration des classes


class DB:

    __slots__ = ['_connectStr', '_connection', '_cursor', ]

    def __init__(self):
        self.__release()
        if DEBUG:
            print('Initialisation de la classe %s' %
            self.__class__.__name__)

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
        if type(connection) == pg._psycopg.connection:  # @UndefinedVariable
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
        if type(cursor) == pg._psycopg.cursor:  # @UndefinedVariable
            self._cursor = cursor
        else:
            raise TypeError('Erreur de type : type %s fourni en argument'
                            % type(cursor))


class HardView(DB):

    __slots__ = ['vmProperties', '_schema', '_tablesRecords',
                 '_tablesObjects']

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

    ## Méthodes d'instances
    def recieve_data(self, vmProperties):
        """
        Cette fonction reçoit les données globales (vmProperties) concernant
        les machines virtuelles (vm), les différencie selon des méthodes
        propres à chacune des tables destinatrices référencées dans le diction-
        naire d'association des tables (_class_assoc) avec leur classe respec-
        tive et,les stocke dans un dictionnaire (_tablesRecords) en attendant
        leur traitement.
        """
        if DEBUG:
            print('Réception des données par la classe %s' %
            self.__class__.__name__)
        for aTable in self._class_assoc.keys():
            if not aTable == 'order':
                oTable = self._tablesObjects[aTable]
                if DEBUG:
                    print('Distribution des données pour la classe %s' %
                    oTable.__class__.__name__)
                """
                if aTable == 'tb_hosts':
                    properties = vmProperties
                elif aTable == 'tb_devs':
                    properties = oTable.get_dict_properties(vmProperties)
                """
                properties = oTable.get_dict_properties(vmProperties)

                if properties:
                    self._tablesRecords[aTable] = \
                    oTable.recieve_data(properties)

    def insert_data(self, withCommit=True):
        """
        Cette fonction ordonne à chaque instance de table d'effectuer selon
        leurs comportements propres, l'insertion et/ou la mise à jour
        respectives des enregistrements des tables de la base de données.
        """
        for aTable in self._class_assoc['order']:
            if self._tablesRecords[aTable]:
                if DEBUG:
                    print('Insertion des données dans la table %s' %
                          aTable)
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
        self.__release()
        for aTable, cTable in self._class_assoc.items():
            if not aTable == 'order':
                oTable = cTable()
                if DEBUG:
                    print('Ajout du couple {%s:%s}'
                          ' au dictionnaire _tablesObjects' %
                    (aTable, str(oTable)))
                oTable.schema = arg
                oTable.connection = self.connection
                if DEBUG:
                    print('Nom du schema %s' % oTable.schema)
                self._tablesObjects[aTable] = oTable


class Table(metaclass=abc.ABCMeta):

    __slots__ = ['records', '_fields', '_fieldsAssoc', '_schema',
                 '_strInsSql', '_cursor', '_connection',
                 '_update_records', '_updateKeys', '_insert_records',
                 '_lost_records']

    fieldsName = ()
    fieldsType = ()
    modes = {'insert': ()}
    _injected_references = ()

    def __init__(self, connection=None):
        if DEBUG:
            print('Initialisation de la classe %s' %
                  self.__class__.__name__)
        self.__release()
        self._connection = connection

    def __release(self):
        self.records = ()  # stockage des records ((a,b,c,d),...)
        self._insert_records = ()
        self._update_records = ()
        self._lost_records = ()
        self._fields = {}
        self._fieldsAssoc = {}
        # self.schema = 'public'
        self._strInsSql = ''
        self._cursor = None

    ## Méthodes d'instance
    def recieve_data(self, data):
        """Réception et stockage des données dans la variable 'records'."""
        if DEBUG:
            print('Réception des données par la classe %s' %
            self.__class__.__name__)
        self.records = ()
        for record in data:
            if DEBUG:
                print('Ajout pour la table %s de l\'enregistrement %s '
                      % (self.name, record))
            values = ()
            for field in self.fieldsName:
                fType = self.fields[field]
                fieldValue = record[self.fieldsAssoc[field]]
                if type(fieldValue) == fType:
                    values += (fieldValue,)
                else:
                    raise TypeError('Erreur de type :\n'
                                    'champs %s de type %s\n'
                                    'valeur fournie %s de type %s' %
                                    (field, fType, fieldValue,
                                    type(fieldValue)))
            self.records += (values,)
        self.distribute_record()
        return self.records

    def insert_data(self, withCommit=True):
        if DEBUG:
            print('Shema %s. Exécution de l\'instruction SQL : %s' % \
            (self.schema, self.sqlInsertInstruction))
        if self.sqlInsertInstruction:
            self.cursor.execute(self.sqlInsertInstruction)
        if self._update_records:
            self.update_data()
        if withCommit:
            self.connection.commit()
        self.sqlInsertInstruction = ''

    def update_data(self, withCommit=True):
        for record in self._update_records:
            setValues = ("{0} = '{1}'".format(field, value) for field, value
                          in dict(zip(self.fieldsName, record)).items()
                          if not field == self.modes['update'])
            strSetValues = str(tuple(setValues))[1:-1].replace('"', '')
            # récupération de l'indexe de la clé d'update
            index = self.fieldsName.index(self.modes['update'])
            sqlUpdInstruction = "UPDATE {0}.{1} SET {2} WHERE {3} = {4};" \
                                .format(self.schema, self.name, strSetValues,
                                        self.modes['update'], record[index])
            self.cursor.execute(sqlUpdInstruction)

    def distribute_record(self):
        if 'update' in self.modes.keys():
            for record in self.records:
                    index = self.fieldsName.index(self.modes['update'])
                    if not (record[index] in self.updateKeys):
                        self._insert_records += (record,)
                    elif not (record in self._update_records):
                        self._update_records += (record,)
                    else:
                        self._lost_records += (record,)
        else:
            self._insert_records = self.records

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
    def cursor(self):
        if not self._cursor:
            self._cursor = self.connection.cursor()
        return self._cursor

    @cursor.setter
    def cursor(self, arg):
        self._cursor = arg

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
            self._fieldsAssoc = dict(zip(self.fieldsName,
                                         self.vPropsName))
        return self._fieldsAssoc

    @fieldsAssoc.setter
    def fieldsAssoc(self, arg):
        pass

    @property
    def sqlInsertInstruction(self):
        if self._insert_records and not self._strInsSql:
            strValues = str(self._insert_records)[1:-1]
            strValues = strValues.strip(',')
            strFields = str(self.fieldsName). \
            replace('\'', '')
            self._strInsSql = "INSERT INTO {0}.{1} {2} VALUES {3};". \
            format(self.schema, self.name, strFields, strValues)
        elif self._insert_records:
            self._strInsSql = ''
            return self.sqlInsertInstruction
        return self._strInsSql

    @sqlInsertInstruction.setter
    def sqlInsertInstruction(self, strSql):
        self._strInsSql = strSql

    @property
    def updateKeys(self):
        #print('Propriétés mor_key')
        if not self._updateKeys:
            self.cursor.execute('SELECT mor FROM {0}.{1};'.
                                format(self.schema, self.name))
            self._updateKeys = tuple(a[0] for a in self.cursor.fetchall())
        return self._updateKeys

    @updateKeys.setter
    def updateKeys(self, arg):
        self._updateKeys = arg

    @abc.abstractmethod
    def get_dict_properties(self, vmProperties):
        return


class TbHosts(Table):

    name = 'tb_hosts'
    fieldsName = ('os', 'mor', 'hostname', 'name', 'cpu', 'memory')
    vPropsName = ('guest_id', 'mor', 'hostname', 'name', 'cpu',
                  'memory_mb')
    fieldsType = (str, int, str, str, int, int)
    modes = {'insert': '', 'update': 'mor'}

    def __init__(self, dbManager=None):
        Table.__init__(self, dbManager)
        self._updateKeys = None

    ## Méthodes d'instance
    def get_dict_properties(self, vmProperties):
        properties = vmProperties
        return properties


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
        """Retourner les dictionnaires des valeurs associées aux propriétés."""
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

    data = [{'guest_id': 'ubu64', 'mor': 45632,
            'name': 'tititi', 'hostname': 'ubutiti', 'cpu': 2,
            'memory_mb':1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu64', 'mor': 1254,
            'name': 'tototo', 'hostname': 'ubutoto', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 2', 30971820, 5494087),
            ('Disque dur 3', 30971820, 5494087)]},
            {'guest_id': 'ubu64', 'mor': 5847,
            'name': 'tata', 'hostname': 'ubutata', 'cpu': 2,
            'memory_mb': 1024, 'disks': [('Disque dur 2', 30971820, 5494087),
            ('Disque dur 5', 30971820, 5494087)]},
            {'guest_id': 'ubu64', 'mor': 47732,
            'name': 'tutotu', 'hostname': 'ubututu', 'cpu': 2,
            'memory_mb':1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu32', 'mor': 47799,
            'name': 'tutytu', 'hostname': 'ubutytu', 'cpu': 2,
            'memory_mb':1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'ubu64', 'mor': 472229,
            'name': 'tutrrrtu', 'hostname': 'ubuyotou', 'cpu': 2,
            'memory_mb':1024, 'disks': [('Disque dur 1', 20971520, 8494080)]},
            {'guest_id': 'W732', 'mor': 411129,
            'name': 'zszsezdeu', 'hostname': 'ezlfjezklje', 'cpu': 2,
            'memory_mb':1024, 'disks': [('Disque dur 1', 20971520, 8494080)]}]

    for arg in ('test', 'public'):
        db.schema = arg
        oTable = db.get_table_byname('tb_hosts')
        oTable.delete_all_records_table(True)

    for arg in ('test', 'public'):
        db.schema = arg
        db.recieve_data(data)
        db.insert_data()

    print(db.get_table_name_list())
    print(db.get_table_records_byname('tb_hosts'))
    oTable = db.get_table_byname('tb_hosts')
    print(oTable.updateKeys)
    db.close_connection()
