from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from django import forms

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


# State Resource (No changes needed)
class StateResource(resources.ModelResource):
    class Meta:
        model = State


# changes
class DepartmentResource(resources.ModelResource):
    state = fields.Field(column_name='state', attribute='state', widget=SafeForeignKeyWidget(State, 'state_name'))
    
    class Meta:
        model = Department
        export_order = ('id', 'dept_name', 'state')

class DivisionResource(resources.ModelResource):
    state = fields.Field(column_name='state', attribute='state', widget=SafeForeignKeyWidget(State, 'state_name'))
    
    class Meta:
        model = Division
        export_order = ('id', 'div_name', 'state')

class DistrictResource(resources.ModelResource):
    division = fields.Field(column_name='division', attribute='division', widget=SafeForeignKeyWidget(Division, 'div_name'))
    state = fields.Field(attribute='division__state__state_name', column_name='state')
    
    class Meta:
        model = District
        export_order = ('id', 'dist_name', 'division', 'state')
    
    def before_import_row(self, row, **kwargs):
        # Existing implementation remains
        division_name = row.get('division')
        state_name = row.get('state')
        if division_name and state_name:
            state, _ = State.objects.get_or_create(state_name=state_name.strip())
            division, _ = Division.objects.get_or_create(div_name=division_name.strip(), state=state)
            row['division'] = division

class TehsilResource(resources.ModelResource):
    district = fields.Field(
        column_name='district',
        attribute='district',
        widget=SafeForeignKeyWidget(District, 'dist_name')
    )
    division = fields.Field(attribute='district__division__div_name', column_name='division')
    state = fields.Field(attribute='district__division__state__state_name', column_name='state')
    
    class Meta:
        model = Tehsil
        export_order = ('id', 'state', 'division', 'district', 'tehsil_name')
    
    def before_import_row(self, row, **kwargs):
        # Existing implementation remains
        district_name = row.get('district')
        division_name = row.get('division')
        state_name = row.get('state')
        
        if state_name and division_name and district_name:
            state, _ = State.objects.get_or_create(state_name=state_name.strip())
            division, _ = Division.objects.get_or_create(div_name=division_name.strip(), state=state)
            district, _ = District.objects.get_or_create(dist_name=district_name.strip(), division=division)
            row['district'] = district.dist_name

class VillageResource(resources.ModelResource):
    district = fields.Field(column_name='district', attribute='district', widget=SafeForeignKeyWidget(District, 'dist_name'))
    tehsil = fields.Field(column_name='tehsil', attribute='tehsil', widget=SafeForeignKeyWidget(Tehsil, 'tehsil_name'))
    division = fields.Field(attribute='district__division__div_name', column_name='division')
    state = fields.Field(attribute='district__division__state__state_name', column_name='state')
    
    class Meta:
        model = Village
        export_order = ('id', 'state', 'division', 'district', 'tehsil', 'vill_name', 'area')
    
    def before_import_row(self, row, **kwargs):
        # Existing implementation remains
        district_name = row.get('district')
        tehsil_name = row.get('tehsil')
        division_name = row.get('division')
        state_name = row.get('state')
        
        if state_name and division_name and district_name and tehsil_name:
            state, _ = State.objects.get_or_create(state_name=state_name.strip())
            division, _ = Division.objects.get_or_create(div_name=division_name.strip(), state=state)
            district, _ = District.objects.get_or_create(dist_name=district_name.strip(), division=division)
            tehsil, _ = Tehsil.objects.get_or_create(tehsil_name=tehsil_name.strip(), district=district)
            row['district'] = district.dist_name
            row['tehsil'] = tehsil.tehsil_name


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
#         widget=ForeignKeyWidget(Office, field='office__office_name')  # Match office by name
#     )
#     post_name = fields.Field(
#         column_name='post_name',
#         attribute='post_name'
#     )
#     post_number = fields.Field(
#         column_name='post_number',
#         attribute='post_number'
#     )

#     class Meta:
#         model = Post
#         skip_unchanged = True
#         report_skipped = True
#         exclude = ('id',)  # Remove ID from imports
#         import_id_fields = ()  # No identifier fields needed
#         fields = ('post_name', 'post_type', 'post_number', 'in_office')

#     def before_import_row(self, row, **kwargs):
#         # Convert office name to ID
#         office_name = row.get('in_office')
#         if office_name:
#             office = Office.objects.filter(office__office_name=office_name).first()
#             if office:
#                 row['in_office'] = office.id

# class PostResource(resources.ModelResource):
#     in_office = fields.Field(
#         column_name='in_office',
#         attribute='in_office',
#         widget=ForeignKeyWidget(Office, field='office__office_name__iexact')  # Case-insensitive match
#     )

#     class Meta:
#         model = Post
#         exclude = ('id',)
#         import_id_fields = ()
#         fields = ('post_name', 'post_type', 'post_number', 'in_office')

#     def before_import_row(self, row, **kwargs):
#         office_name = row.get('in_office')
#         if office_name:
#             # Clean and find office
#             office_name_clean = office_name.strip().lower()
#             office = Office.objects.filter(
#                 office__office_name__iexact=office_name_clean  # Case-insensitive search
#             ).first()
            
#             if not office:
#                 # Create minimal Office if allowed (adjust as needed)
#                 # WARNING: Requires default values for other fields!
#                 office_name_obj, _ = OfficeName.objects.get_or_create(
#                     office_name=office_name.strip()
#                 )
#                 district = District.objects.first()  # Replace with actual logic
#                 office = Office.objects.create(
#                     office=office_name_obj,
#                     district=district,
#                     place="Default Place"  # Provide required field
#                 )
            
#             row['in_office'] = office.id

#chatgpt
# class PostResource(resources.ModelResource):
#     in_office = fields.Field(
#         column_name='office_number',  # Match office_number from Excel file
#         attribute='in_office',
#         widget=ForeignKeyWidget(Office, field='office_number')
#     )

#     class Meta:
#         model = Post
#         exclude = ('id',)
#         import_id_fields = ()
#         fields = ('post_name', 'post_type', 'post_number', 'in_office')

#     def before_import_row(self, row, **kwargs):
#         office_number = row.get('office_number')  # Read office_number from Excel

#         if office_number:
#             try:
#                 # Get the Office instance using office_number
#                 office = Office.objects.get(office_number=office_number)
#                 row['in_office'] = office.id  # Assign the correct Office ID
#             except Office.DoesNotExist:
#                 raise ValueError(f"Office with office_number {office_number} does not exist.")

# deepseek
# class PostResource(resources.ModelResource):
#     in_office = fields.Field(
#         column_name='in_office',  # Match Excel column header
#         attribute='in_office',
#         widget=ForeignKeyWidget(Office, field='office_number')  # Use office_number for lookup
#     )

#     class Meta:
#         model = Post
#         fields = ('post_name', 'post_type', 'post_number', 'in_office')
#         import_id_fields = ()
#         skip_unchanged = True

#     def before_import_row(self, row, **kwargs):
#         office_number = row.get('in_office')  # Get value from Excel's "in_office" column
        
#         if office_number:
#             try:
#                 # Convert to integer (Excel might store numbers as strings)
#                 office_number = int(office_number)
#                 # Find Office by office_number
#                 office = Office.objects.get(office_number=office_number)
#                 row['in_office'] = office.id
#             except Office.DoesNotExist:
#                 raise ValueError(f"Office with number {office_number} does not exist. Import Offices first.")
#             except ValueError:
#                 raise ValueError(f"Invalid office number: {office_number}")

# class PostResource(resources.ModelResource):
#     in_office = fields.Field(
#         column_name='in_office',  # Match Excel column name
#         attribute='in_office',
#         widget=ForeignKeyWidget(Office, field='office_number')  # Directly use office_number for lookup
#     )

#     class Meta:
#         model = Post
#         fields = ('post_name', 'post_type', 'post_number', 'in_office')
#         import_id_fields = ()
#         skip_unchanged = True

#     # REMOVE THE before_import_row METHOD

# admin.py
class PostResource(resources.ModelResource):
    in_office = fields.Field(
        column_name='in_office',
        attribute='in_office',
        widget=ForeignKeyWidget(Office, field='office_number')
    )

    post_name = fields.Field(
        column_name='post_name',
        attribute='post_name',
        widget=forms.widgets.Select(choices=Post.POST_CHOICES)  # Force validation
    )

    post_type = fields.Field(
        column_name='post_type',
        attribute='post_type',
        widget=forms.widgets.Select(choices=Post.POST_TYPE_CHOICES)
    )

    class Meta:
        model = Post
        fields = ('post_name', 'post_type', 'post_number', 'in_office')
        import_id_fields = ()

    def before_import_row(self, row, **kwargs):
        # Normalize post_name
        row['post_name'] = row['post_name'].strip().lower()
        
        # Normalize post_type
        row['post_type'] = row['post_type'].strip().lower()

        # Handle office_number
        office_number = row.get('in_office')
        if office_number:
            try:
                office = Office.objects.get(office_number=int(office_number))
                row['in_office'] = office.id
            except Office.DoesNotExist:
                raise ValueError(f"Office {office_number} not found")
            except ValueError:
                raise ValueError(f"Invalid office number: {office_number}")

# Register resources with updated configurations
@admin.register(State)
class StateAdmin(ImportExportModelAdmin):
    resource_class = StateResource
    list_display = ('state_name',)
    list_filter = ('state_name',)
    search_fields = ('state_name',)

@admin.register(Division)
class DivisionAdmin(ImportExportModelAdmin):
    resource_class = DivisionResource
    list_display = ('div_name', 'state')
    list_filter = ('state',)
    search_fields = ('div_name', 'state__state_name')

@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    resource_class = DistrictResource
    list_display = ('dist_name', 'division')
    list_filter = ('division',)
    search_fields = ('dist_name', 'division__div_name')

@admin.register(Tehsil)
class TehsilAdmin(ImportExportModelAdmin):
    resource_class = TehsilResource
    list_display = ('tehsil_name', 'district')
    list_filter = ('district',)
    search_fields = ('tehsil_name', 'district__dist_name')

@admin.register(Village)
class VillageAdmin(ImportExportModelAdmin):
    resource_class = VillageResource
    list_display = ('vill_name', 'district', 'tehsil', 'area')
    list_filter = ('district', 'tehsil', 'area')
    search_fields = ('vill_name', 'district__dist_name', 'tehsil__tehsil_name')

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

# Remaining models can stay with default ImportExportModelAdmin
# admin.site.register(Department, ImportExportModelAdmin)
# admin.site.register(SubDepartment, ImportExportModelAdmin)
@admin.register(SubDepartment)
class SubDepartmentAdmin(ImportExportModelAdmin):
    list_display = ('sub_dept_name', 'department')
    list_filter = ('department',)
    search_fields = ('sub_dept_name', 'department__dept_name')

# admin.site.register(Office, ImportExportModelAdmin)
@admin.register(SubOffice)
class SubOfficeAdmin(ImportExportModelAdmin):
    list_display = ('name', 'upper_office', 'tehsil')
    list_filter = ('upper_office', 'tehsil')
    search_fields = ('name', 'upper_office__office__office_name', 'tehsil__tehsil_name')

# admin.site.register(Post, ImportExportModelAdmin)
# @admin.register(Post)
# class PostAdmin(ImportExportModelAdmin):
#     list_display = ('post_name', 'post_type', 'in_office')
#     list_filter = ('post_type', 'in_office')
#     search_fields = ('post_name', 'in_office__office__office_name')

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

@admin.register(Employee)
class EmployeeAdmin(ImportExportModelAdmin):
    list_display = ('name', 'employeeID', 'current_office')
    list_filter = ('current_office', 'home_district')
    search_fields = ('name', 'employeeID', 'current_office__office__office_name')

@admin.register(TransferPrevious)
class TransferPreviousAdmin(ImportExportModelAdmin):
    list_display = ('order_no', 'employee', 'old_office', 'new_office')
    list_filter = ('old_office', 'new_office')
    search_fields = ('order_no', 'employee__name')

@admin.register(History)
class HistoryAdmin(ImportExportModelAdmin):
    list_display = ('employee', 'from_date', 'to_date')
    list_filter = ('from_date', 'to_date')
    search_fields = ('employee__name',)

@admin.register(TransferList)
class TransferListAdmin(ImportExportModelAdmin):
    list_display = ('employee', 'current_office', 'new_office')
    list_filter = ('current_office', 'new_office')
    search_fields = ('employee__name',)