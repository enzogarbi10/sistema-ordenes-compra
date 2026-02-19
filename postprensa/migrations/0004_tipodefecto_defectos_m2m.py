from django.db import migrations, models


def migrate_boolean_defects_to_m2m(apps, schema_editor):
    """Create TipoDefecto entries and migrate existing boolean data to M2M."""
    TipoDefecto = apps.get_model('postprensa', 'TipoDefecto')
    ControlCalidad = apps.get_model('postprensa', 'ControlCalidad')

    # Create the 4 default defect types
    impresion, _ = TipoDefecto.objects.get_or_create(nombre='Impresión')
    stamping, _ = TipoDefecto.objects.get_or_create(nombre='Stamping')
    relieve, _ = TipoDefecto.objects.get_or_create(nombre='Relieve')
    serigrafia, _ = TipoDefecto.objects.get_or_create(nombre='Serigrafía')

    # Migrate existing data
    for control in ControlCalidad.objects.all():
        if control.defecto_impresion:
            control.defectos.add(impresion)
        if control.defecto_stamping:
            control.defectos.add(stamping)
        if control.defecto_relieve:
            control.defectos.add(relieve)
        if control.defecto_serigrafia:
            control.defectos.add(serigrafia)


class Migration(migrations.Migration):

    dependencies = [
        ('postprensa', '0003_maquinista_operarioinspeccion_and_more'),
    ]

    operations = [
        # Step 1: Create TipoDefecto model
        migrations.CreateModel(
            name='TipoDefecto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100, unique=True, verbose_name='Nombre')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Tipo de Defecto',
                'verbose_name_plural': 'Tipos de Defecto',
                'ordering': ['nombre'],
            },
        ),

        # Step 2: Add M2M field
        migrations.AddField(
            model_name='controlcalidad',
            name='defectos',
            field=models.ManyToManyField(blank=True, to='postprensa.tipodefecto', verbose_name='Tipos de Defecto'),
        ),

        # Step 3: Migrate data from booleans to M2M
        migrations.RunPython(migrate_boolean_defects_to_m2m, migrations.RunPython.noop),

        # Step 4: Remove old boolean fields
        migrations.RemoveField(model_name='controlcalidad', name='defecto_impresion'),
        migrations.RemoveField(model_name='controlcalidad', name='defecto_stamping'),
        migrations.RemoveField(model_name='controlcalidad', name='defecto_relieve'),
        migrations.RemoveField(model_name='controlcalidad', name='defecto_serigrafia'),
    ]
