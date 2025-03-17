from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django import forms
from import_export import widgets

class SafeForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            obj, created = self.model.objects.get_or_create(**{self.field: value.strip()})
            return obj
        return None

class OfficeNameForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        department_name = row.get('department')
        if not value or not department_name:
            return None
        # Get or create Department
        department, _ = Department.objects.get_or_create(dept_name=department_name.strip())
        # Get or create OfficeName using BOTH office_name and department
        obj, _ = OfficeName.objects.get_or_create(
            office_name=value.strip(),
            department=department
        )
        return obj

class StateResource(resources.ModelResource):
    class Meta:
        model = State

class OfficeNameResource(resources.ModelResource):
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=SafeForeignKeyWidget(Department, 'dept_name')
    )

    class Meta:
        model = OfficeName
        export_order = ('id', 'office_name', 'department')
        import_id_fields = ('office_name', 'department')  # Use both fields to identify existing records

    def before_import_row(self, row, **kwargs):
        dept_name = row.get('department')
        
        if dept_name:
            department, _ = Department.objects.get_or_create(dept_name=dept_name.strip()) #, district=district
            row['department'] = department.dept_name

class OfficeResource(resources.ModelResource):
    office = fields.Field(
        column_name='office',
        attribute='office',
        widget=OfficeNameForeignKeyWidget(OfficeName, 'office_name')
    )
    department = fields.Field(
        column_name='department',
        attribute='office__department__dept_name'  # Add department field for export
    ) 
    state = fields.Field(
        column_name='state',
        attribute='office__department__state__state_name'
    )   
    district = fields.Field(
        column_name='district',
        attribute='district',
        widget=SafeForeignKeyWidget(District, 'dist_name')
    )
    division = fields.Field(attribute='district__division__div_name', column_name='division')
    state = fields.Field(attribute='district__division__state__state_name', column_name='state')
    tehsil = fields.Field(
        column_name='tehsil',
        attribute='tehsil',
        widget=SafeForeignKeyWidget(Tehsil, 'tehsil_name'),
    )

    class Meta:
        model = Office
        fields = ('id', 'office_number', 'office', 'department', 'state', 'district', 'tehsil', 'place')
        import_id_fields = ('office_number',)
        export_order = ('id', 'office_number', 'office', 'department', 'state', 'district', 'division', 'state', 'tehsil', 'place')

    def before_import_row(self, row, **kwargs):
        # Ensure District hierarchy is created
        dist_name = row.get('district')
        state_name = row.get('state')
        div_name = row.get('division')

        if state_name and div_name and dist_name:
            state, _ = State.objects.get_or_create(state_name=state_name.strip())
            division, _ = Division.objects.get_or_create(div_name=div_name.strip(), state=state)
            district, _ = District.objects.get_or_create(dist_name=dist_name.strip(), division=division)
            row['district'] = district.dist_name  # Let widget resolve district by name

        # Handle Tehsil
        tehsil_name = row.get('tehsil')
        if tehsil_name and dist_name:
            district = District.objects.get(dist_name=dist_name.strip())
            tehsil, _ = Tehsil.objects.get_or_create(tehsil_name=tehsil_name.strip(), district=district)
            row['tehsil'] = tehsil.tehsil_name

# class PostResource(resources.ModelResource):
#     in_office = fields.Field(
#         column_name='in_office',
#         attribute='in_office',
#         widget=ForeignKeyWidget(Office, field='office_number')
#     )

#     post_name = fields.Field(
#         column_name='post_name',
#         attribute='post_name',
#         widget=forms.widgets.Select(choices=Post.POST_CHOICES)  # Force validation
#     )

#     post_type = fields.Field(
#         column_name='post_type',
#         attribute='post_type',
#         widget=forms.widgets.Select(choices=Post.POST_TYPE_CHOICES)
#     )

#     class Meta:
#         model = Post
#         fields = ('post_name', 'post_type', 'post_number', 'in_office')
#         import_id_fields = ()

#     def before_import_row(self, row, **kwargs):
#         # Normalize post_name
#         row['post_name'] = row['post_name'].strip().lower()
        
#         # Normalize post_type
#         row['post_type'] = row['post_type'].strip().lower()

#         # Handle office_number
#         office_number = row.get('in_office')
#         if office_number:
#             try:
#                 office = Office.objects.get(office_number=int(office_number))
#                 row['in_office'] = office.id
#             except Office.DoesNotExist:
#                 raise ValueError(f"Office {office_number} not found")
#             except ValueError:
#                 raise ValueError(f"Invalid office number: {office_number}")

class OfficeForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        print(f"Processing in_office value: {value}")  # Debugging
        if not value:
            print("No value provided for in_office.")
            return None

        # Attempt to find by office_number (integer)
        try:
            office_number = int(value)
            print(f"Looking up by office_number: {office_number}")
            office = self.model.objects.get(office_number=office_number)
            print(f"Found office by number: {office}")
            return office
        except ValueError:
            print(f"Value '{value}' is not a number. Trying office name.")
        except self.model.DoesNotExist:
            print(f"No office found with number {value}. Trying office name.")

        # Attempt to find by office name (OfficeName's office_name)
        try:
            office_name = value.strip()
            print(f"Looking up by office name: {office_name}")
            office = self.model.objects.get(office__office_name__iexact=office_name)
            print(f"Found office by name: {office}")
            return office
        except self.model.DoesNotExist:
            print(f"No office found with name '{office_name}'.")
            raise ValueError(f"Office '{value}' not found.")
        except self.model.MultipleObjectsReturned:
            print(f"Multiple offices with name '{office_name}'. Using first.")
            return self.model.objects.filter(office__office_name__iexact=office_name).first()

# Update the PostResource class
class PostResource(resources.ModelResource):
    in_office = fields.Field(
        column_name='in_office',
        attribute='in_office',
        widget=OfficeForeignKeyWidget(Office)  # Use custom widget
    )

    post_name = fields.Field(
        column_name='post_name',
        attribute='post_name',
        widget=widgets.ChoiceWidget(choices=Post.POST_CHOICES)  # Correct widget
    )

    post_type = fields.Field(
        column_name='post_type',
        attribute='post_type',
        widget=widgets.ChoiceWidget(choices=Post.POST_TYPE_CHOICES)  # Correct widget
    )

    class Meta:
        model = Post
        fields = ('post_name', 'post_type', 'post_number', 'in_office')
        import_id_fields = ()

    def before_import_row(self, row, **kwargs):
        # Normalize post_name and post_type
        row['post_name'] = row.get('post_name', '').strip().lower()
        row['post_type'] = row.get('post_type', '').strip().lower()
        # No need to handle 'in_office' here; widget handles it

# Register resources with updated configurations
@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    resource_class = DistrictResource
    list_display = ('dist_name', 'division')
    list_filter = ('division',)
    search_fields = ('dist_name', 'division__div_name')

@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource
    list_display = ('dept_name', 'state')
    list_filter = ('state',)
    search_fields = ('dept_name', 'state__state_name')

@admin.register(OfficeName)
class OfficeNameAdmin(ImportExportModelAdmin):
    resource_class = OfficeNameResource
    list_display = ('office_name', 'department')
    list_filter = ('department', 'office_name')
    search_fields = ('office_name', 'department__dept_name')

@admin.register(Office)
class OfficeAdmin(ImportExportModelAdmin):
    resource_class = OfficeResource
    list_display = ('office_number', 'get_office_name', 'get_department', 'get_state', 'district', 'place')
    # Add fields to the change form
    fieldsets = (
        ('Office Details', {
            'fields': (
                'office_number', 
                'office', 
                ('get_department', 'get_state'),  # Group related fields
                'district', 
                'tehsil', 
                'place'
            )
        }),
    )
    readonly_fields = ('get_department', 'get_state')  # Make them non-editable

    # Enable sorting for custom fields
    def get_office_name(self, obj):
        return obj.office.office_name
    get_office_name.short_description = 'Office Name'
    get_office_name.admin_order_field = 'office__office_name'  # Enable sorting
    
    def get_department(self, obj):
        return obj.office.department.dept_name if obj.office else None
    get_department.short_description = 'Department'
    get_department.admin_order_field = 'office__department__dept_name'  # Enable sorting

    def get_state(self, obj):
        return obj.office.department.state.state_name if (obj.office and obj.office.department) else None
    get_state.short_description = 'State'
    get_state.admin_order_field = 'office__department__state__state_name'    

    # Proper filter configuration
    list_filter = (
        'office_number',
        ('office__office_name', admin.AllValuesFieldListFilter),
        ('office__department', admin.RelatedFieldListFilter),
        'district',
        'place'
    )
    
    # Search configuration
    search_fields = (
        'office_number',
        'office__office_name',
        'office__department__dept_name',
        'district__dist_name',
        'place'
    )

    def get_office_name(self, obj):
        return obj.office.office_name if obj.office else None
    get_office_name.short_description = 'Office Name'

    def get_department(self, obj):
        return obj.office.department.dept_name if obj.office and obj.office.department else None
    get_department.short_description = 'Department'



@admin.register(Post)
class PostAdmin(ImportExportModelAdmin):
    resource_class = PostResource
    list_display = ('post_name', 'post_type', 'post_number', 'in_office', 'get_office_department')
    list_filter = ('post_type', 'in_office', 'post_number')
    search_fields = (
        'post_name',
        'in_office__office__office_name',
        'post_number'
    )
    autocomplete_fields = ['in_office']  # Add office search

    def get_office_department(self, obj):
        return obj.in_office.office.department if obj.in_office else None
    get_office_department.short_description = 'Department'
