from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

class SafeForeignKeyWidget(ForeignKeyWidget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            obj, created = self.model.objects.get_or_create(**{self.field: value.strip()})
            return obj
        return None

# State Resource (No changes needed)
class StateResource(resources.ModelResource):
    class Meta:
        model = State

# # Division Resource (No changes needed)
# class DivisionResource(resources.ModelResource):
#     state = fields.Field(column_name='state', attribute='state', widget=SafeForeignKeyWidget(State, 'state_name'))
#     class Meta:
#         model = Division

# # District Resource (Already correct)
# class DistrictResource(resources.ModelResource):
#     division = fields.Field(column_name='division', attribute='division', widget=SafeForeignKeyWidget(Division, 'div_name'))
#     class Meta:
#         model = District

#     def before_import_row(self, row, **kwargs):
#         division_name = row.get('division')
#         state_name = row.get('state')
#         if division_name and state_name:
#             state, _ = State.objects.get_or_create(state_name=state_name.strip())
#             division, _ = Division.objects.get_or_create(div_name=division_name.strip(), state=state)
#             row['division'] = division

# # Tehsil Resource (Updated to handle parent dependencies)
# class TehsilResource(resources.ModelResource):
#     district = fields.Field(
#         column_name='district',
#         attribute='district',
#         widget=SafeForeignKeyWidget(District, 'dist_name')
#     )
    
#     class Meta:
#         model = Tehsil
    
#     def before_import_row(self, row, **kwargs):
#         district_name = row.get('district')
#         division_name = row.get('division')
#         state_name = row.get('state')
        
#         # Create parent models if they exist in the row
#         if state_name and division_name and district_name:
#             state, _ = State.objects.get_or_create(state_name=state_name.strip())
#             division, _ = Division.objects.get_or_create(div_name=division_name.strip(), state=state)
#             district, _ = District.objects.get_or_create(dist_name=district_name.strip(), division=division)
#             row['district'] = district.dist_name  # Ensure the district name is correctly set

# # Village Resource (Update to handle dependencies)
# class VillageResource(resources.ModelResource):
#     district = fields.Field(column_name='district', attribute='district', widget=SafeForeignKeyWidget(District, 'dist_name'))
#     tehsil = fields.Field(column_name='tehsil', attribute='tehsil', widget=SafeForeignKeyWidget(Tehsil, 'tehsil_name'))
    
#     class Meta:
#         model = Village
    
#     def before_import_row(self, row, **kwargs):
#         # Handle Village dependencies similar to Tehsil
#         district_name = row.get('district')
#         tehsil_name = row.get('tehsil')
#         division_name = row.get('division')
#         state_name = row.get('state')
        
#         if state_name and division_name and district_name and tehsil_name:
#             state, _ = State.objects.get_or_create(state_name=state_name.strip())
#             division, _ = Division.objects.get_or_create(div_name=division_name.strip(), state=state)
#             district, _ = District.objects.get_or_create(dist_name=district_name.strip(), division=division)
#             tehsil, _ = Tehsil.objects.get_or_create(tehsil_name=tehsil_name.strip(), district=district)
#             row['district'] = district.dist_name
#             row['tehsil'] = tehsil.tehsil_name


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

class OfficeResource(resources.ModelResource):
    department = fields.Field(
        column_name='department',
        attribute='department',
        widget=SafeForeignKeyWidget(Department, 'dept_name')
    )
    district = fields.Field(attribute='department__district__dist_name', column_name='district')
    division = fields.Field(attribute='department__district__division__div_name', column_name='division')
    state = fields.Field(attribute='department__district__division__state__state_name', column_name='state')

    class Meta:
        model = Office
        export_order = ('office_id', 'office_name', 'state', 'division', 'district', 'department', 'place')
        import_id_fields = ('office_id',)  # Uses office_id as identifier during import
    
    def before_import_row(self, row, **kwargs):
        dept_name = row.get('department')
        dist_name = row.get('district')
        div_name = row.get('division')
        state_name = row.get('state')
        
        if dept_name and dist_name and div_name and state_name:
            # Create parent hierarchy
            state, _ = State.objects.get_or_create(state_name=state_name.strip())
            division, _ = Division.objects.get_or_create(div_name=div_name.strip(), state=state)
            district, _ = District.objects.get_or_create(dist_name=dist_name.strip(), division=division)
            department, _ = Department.objects.get_or_create(dept_name=dept_name.strip(), district=district)
            row['department'] = department.dept_name


# Register resources with updated configurations
@admin.register(State)
class StateAdmin(ImportExportModelAdmin):
    resource_class = StateResource

@admin.register(Division)
class DivisionAdmin(ImportExportModelAdmin):
    resource_class = DivisionResource

@admin.register(District)
class DistrictAdmin(ImportExportModelAdmin):
    resource_class = DistrictResource

@admin.register(Tehsil)
class TehsilAdmin(ImportExportModelAdmin):
    resource_class = TehsilResource

@admin.register(Village)
class VillageAdmin(ImportExportModelAdmin):
    resource_class = VillageResource


@admin.register(Department)
class DepartmentAdmin(ImportExportModelAdmin):
    resource_class = DepartmentResource


@admin.register(Office)
class OfficeAdmin(ImportExportModelAdmin):
    resource_class = OfficeResource
    list_display = ('office_id', 'office_name', 'department', 'place')


# Remaining models can stay with default ImportExportModelAdmin
# admin.site.register(Department, ImportExportModelAdmin)
admin.site.register(SubDepartment, ImportExportModelAdmin)
# admin.site.register(Office, ImportExportModelAdmin)
admin.site.register(SubOffice, ImportExportModelAdmin)
admin.site.register(Post, ImportExportModelAdmin)
admin.site.register(Employee, ImportExportModelAdmin)
admin.site.register(TransferPrevious, ImportExportModelAdmin)
admin.site.register(History, ImportExportModelAdmin)
admin.site.register(TransferList, ImportExportModelAdmin)