from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0003_post_image_alter_post_image_url'),  # or whichever is last
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image_url',
            field=models.URLField(blank=True, null=True, max_length=500),
        ),
    ]