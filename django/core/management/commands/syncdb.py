from django.core.management.base import NoArgsCommand
from django.core.management.color import no_style
from optparse import make_option
import sys

try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--verbosity', action='store', dest='verbosity', default='1',
            type='choice', choices=['0', '1', '2'],
            help='Verbosity level; 0=minimal output, 1=normal output, 2=all output'),
        make_option('--noinput', action='store_false', dest='interactive', default=True,
            help='Tells Django to NOT prompt the user for input of any kind.'),
    )
    help = "Create the database tables for all apps in INSTALLED_APPS whose tables haven't already been created."

    def handle_noargs(self, **options):
        from django.db import connection, transaction, models
        from django.conf import settings
        from django.core.management.sql import table_list, installed_models, sql_model_create, sql_for_pending_references, many_to_many_sql_for_model, custom_sql_for_model, sql_indexes_for_model, emit_post_sync_signal

        verbosity = int(options.get('verbosity', 1))
        interactive = options.get('interactive')

        self.style = no_style()

        # Import the 'management' module within each installed app, to register
        # dispatcher events.
        for app_name in settings.INSTALLED_APPS:
            try:
                __import__(app_name + '.management', {}, {}, [''])
            except ImportError, exc:
                if not exc.args[0].startswith('No module named management'):
                    raise

        cursor = connection.cursor()

        if connection.features.uses_case_insensitive_names:
            table_name_converter = lambda x: x.upper()
        else:
            table_name_converter = lambda x: x
        # Get a list of all existing database tables, so we know what needs to
        # be added.
        tables = [table_name_converter(name) for name in table_list()]

        # Get a list of already installed *models* so that references work right.
        seen_models = installed_models(tables)
        created_models = set()
        pending_references = {}

        # Create the tables for each model
        for app in models.get_apps():
            app_name = app.__name__.split('.')[-2]
            model_list = models.get_models(app)
            for model in model_list:
                # Create the model's database table, if it doesn't already exist.
                if verbosity >= 2:
                    print "Processing %s.%s model" % (app_name, model._meta.object_name)
                if table_name_converter(model._meta.db_table) in tables:
                    continue
                sql, references = sql_model_create(model, self.style, seen_models)
                seen_models.add(model)
                created_models.add(model)
                for refto, refs in references.items():
                    pending_references.setdefault(refto, []).extend(refs)
                    if refto in seen_models:
                        sql.extend(sql_for_pending_references(refto, self.style, pending_references))
                sql.extend(sql_for_pending_references(model, self.style, pending_references))
                if verbosity >= 1:
                    print "Creating table %s" % model._meta.db_table
                for statement in sql:
                    cursor.execute(statement)
                tables.append(table_name_converter(model._meta.db_table))

        # Create the m2m tables. This must be done after all tables have been created
        # to ensure that all referred tables will exist.
        for app in models.get_apps():
            app_name = app.__name__.split('.')[-2]
            model_list = models.get_models(app)
            for model in model_list:
                if model in created_models:
                    sql = many_to_many_sql_for_model(model, self.style)
                    if sql:
                        if verbosity >= 2:
                            print "Creating many-to-many tables for %s.%s model" % (app_name, model._meta.object_name)
                        for statement in sql:
                            cursor.execute(statement)

        transaction.commit_unless_managed()

        # Send the post_syncdb signal, so individual apps can do whatever they need
        # to do at this point.
        emit_post_sync_signal(created_models, verbosity, interactive)

        # Install custom SQL for the app (but only if this
        # is a model we've just created)
        for app in models.get_apps():
            app_name = app.__name__.split('.')[-2]
            for model in models.get_models(app):
                if model in created_models:
                    custom_sql = custom_sql_for_model(model)
                    if custom_sql:
                        if verbosity >= 1:
                            print "Installing custom SQL for %s.%s model" % (app_name, model._meta.object_name)
                        try:
                            for sql in custom_sql:
                                cursor.execute(sql)
                        except Exception, e:
                            sys.stderr.write("Failed to install custom SQL for %s.%s model: %s" % \
                                                (app_name, model._meta.object_name, e))
                            transaction.rollback_unless_managed()
                        else:
                            transaction.commit_unless_managed()

        # Install SQL indicies for all newly created models
        for app in models.get_apps():
            app_name = app.__name__.split('.')[-2]
            for model in models.get_models(app):
                if model in created_models:
                    index_sql = sql_indexes_for_model(model, self.style)
                    if index_sql:
                        if verbosity >= 1:
                            print "Installing index for %s.%s model" % (app_name, model._meta.object_name)
                        try:
                            for sql in index_sql:
                                cursor.execute(sql)
                        except Exception, e:
                            sys.stderr.write("Failed to install index for %s.%s model: %s" % \
                                                (app_name, model._meta.object_name, e))
                            transaction.rollback_unless_managed()
                        else:
                            transaction.commit_unless_managed()

        # Install the 'initial_data' fixture, using format discovery
        from django.core.management import call_command
        call_command('loaddata', 'initial_data', verbosity=verbosity)
