class EgeDatabase:
    
    __instance__ = None
    
    def __init__(self):
        self._subjects = []
    
    def get_storage(self):
        if EgeDatabase.__instance__ is None:
            EgeDatabase.__instance__ = EgeDatabase()
        return EgeDatabase.__instance__

    def create_db(self, conn):
        crs = conn.cursor()
        create = 'CREATE TABLE IF NOT EXISTS'
        tables = \
            """
            PRAGMA foreign_keys = off;
            BEGIN TRANSACTION;
    
            {create} Problem (theme_name INTEGER REFERENCES Theme (name), id INTEGER, text TEXT, solve TEXT, help TEXT, images BLOB);
            {create} Subject (name STRING PRIMARY KEY UNIQUE);
            {create} Task (subject_name STRING REFERENCES Subject (name), name STRING PRIMARY KEY);
            {create} Theme (task_name STRING REFERENCES Task (name), name STRING PRIMARY KEY);
    
            COMMIT TRANSACTION;
            PRAGMA foreign_keys = on;
            """.format(create=create)
        crs.executescript(tables)

    def update(self):
        pass

    def add_subject(self, subject):
        self._subjects.append(subject)

    def add(self, user):
        pass

    def find(self, user_id):
        pass

    def get(self, connection, subject, task=None, theme=None, depth=3):
        if depth > 3:
            depth = 3
        levels = {
            1: 'Task',
            2: 'Theme',
            3: 'Problem'
        }
        crs = connection.cursor()

        def format_arg(arg, ):
            if isinstance(arg, int):
                return arg
            return "'{}'".format(arg)

        execute = \
            ''' 
            SELECT DISTINCT {level}.*
            FROM Subject, Task, Theme, Problem
            WHERE
                Subject.name = '{subject}' AND
                Task.subject_name = Subject.name AND
                Theme.task_name = {task} AND
                Problem.theme_name = {theme}
            '''.format(
                level=levels.get(depth),
                subject=subject if subject else '*',
                task=format_arg(task) if task else 'Task.name',
                theme=format_arg(theme) if theme else 'Theme.name'
            )
        crs.execute(execute)
        return crs.fetchall()

