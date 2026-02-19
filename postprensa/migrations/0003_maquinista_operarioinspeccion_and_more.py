from django.db import migrations, models
import django.db.models.deletion


def migrate_charfield_to_fk(apps, schema_editor):
    """Migrate existing CharField data to FK relationships."""
    ControlCalidad = apps.get_model('postprensa', 'ControlCalidad')
    Maquinista = apps.get_model('postprensa', 'Maquinista')
    OperarioInspeccion = apps.get_model('postprensa', 'OperarioInspeccion')

    # Collect unique maquinista names and create entries
    maquinista_names = ControlCalidad.objects.values_list('operario_old', flat=True).distinct()
    for name in maquinista_names:
        if name and name.strip():
            OperarioInspeccion.objects.get_or_create(nombre=name.strip())

    operario_names = ControlCalidad.objects.values_list('maquinista_old', flat=True).distinct()
    for name in operario_names:
        if name and name.strip():
            Maquinista.objects.get_or_create(nombre=name.strip())

    # Now link each control to the corresponding FK
    for control in ControlCalidad.objects.all():
        if control.maquinista_old and control.maquinista_old.strip():
            control.maquinista = Maquinista.objects.get(nombre=control.maquinista_old.strip())
        if control.operario_old and control.operario_old.strip():
            control.operario = OperarioInspeccion.objects.get(nombre=control.operario_old.strip())
        control.save()


class Migration(migrations.Migration):

    dependencies = [
        ('postprensa', '0002_alter_controlcalidad_orden'),
    ]

    operations = [
        # Step 1: Create the new models
        migrations.CreateModel(
            name='Maquinista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Maquinista',
                'verbose_name_plural': 'Maquinistas',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='OperarioInspeccion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Operario de Inspección',
                'verbose_name_plural': 'Operarios de Inspección',
                'ordering': ['nombre'],
            },
        ),

        # Step 2: Rename old CharField fields
        migrations.RenameField(
            model_name='controlcalidad',
            old_name='maquinista',
            new_name='maquinista_old',
        ),
        migrations.RenameField(
            model_name='controlcalidad',
            old_name='operario',
            new_name='operario_old',
        ),

        # Step 3: Add new FK fields (nullable)
        migrations.AddField(
            model_name='controlcalidad',
            name='maquinista',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='postprensa.maquinista',
                verbose_name='Maquinista',
            ),
        ),
        migrations.AddField(
            model_name='controlcalidad',
            name='operario',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='postprensa.operarioinspeccion',
                verbose_name='Operario Inspección',
            ),
        ),

        # Step 4: Migrate data
        migrations.RunPython(migrate_charfield_to_fk, migrations.RunPython.noop),

        # Step 5: Remove old CharField fields
        migrations.RemoveField(
            model_name='controlcalidad',
            name='maquinista_old',
        ),
        migrations.RemoveField(
            model_name='controlcalidad',
            name='operario_old',
        ),
    ]
