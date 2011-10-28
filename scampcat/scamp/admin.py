from django.contrib import admin

from scampcat.scamp.models import Set, Scamp, Image, Annotation


class SetAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['title', 'slug', 'user', 'description']
    search_fields = ['title', 'slug', 'description']


class AnnotationInlineAdmin(admin.TabularInline):
    model = Annotation
    extra = 3


class ScampAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['slug', 'title', 'user']
    search_fields = ['title', 'slug', 'description']
    inlines = [AnnotationInlineAdmin]


class ImageAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ['id', 'width', 'height', 'url', 'url_key']
    readonly_fields = ['width', 'height', 'url', 'url_key']
    search_fields = ['url', 'url_key']


admin.site.register(Set, SetAdmin)
admin.site.register(Scamp, ScampAdmin)
admin.site.register(Image, ImageAdmin)
