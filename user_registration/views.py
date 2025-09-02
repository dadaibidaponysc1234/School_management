from django.shortcuts import render
from .models import (User,Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     ClassYear,Class,Classroom,ClassDepartment, StudentClass,
                     Student,Teacher,StudentRegistrationPin,
                     )

from .serializers import (CustomTokenObtainPairSerializer, SuperAdminCreateSerializer,SuperAdminSerializer,
                           RoleSerializer,TeacherCreateSerializer,SchoolCreateSerializer,SchoolListSerializer,
                           SubscriptionSerializer,ComplianceVerificationSerializer,
                           MessageSerializer,StudentCreateSerializer,StudentUpdateSerializer,
                           StudentListSerializer,TeacherListSerializer,TeacherUpdateSerializer,StudentDetailSerializer,
                           TeacherDetailSerializer,SchoolAdminCreateSerializer,SchoolAdminListSerializer,
                           SchoolAdminDetailSerializer,SchoolAdminUpdateSerializer,RegistrationPinSerializer)

from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status,generics, permissions, parsers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import (IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,IsClassTeacher,
                          HasValidPinAndSchoolId,IsStudentReadOnly,IsTeacherReadOnly,IsSchoolAdminReadOnly)
from rest_framework.generics import (ListAPIView,RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView,RetrieveUpdateAPIView,DestroyAPIView,RetrieveAPIView)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import generics
from django.db import transaction
from django.utils.crypto import get_random_string
import csv
from io import StringIO
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from .utils import generate_temp_token, validate_temp_token
from django.utils.crypto import get_random_string
import pandas as pd



#Standard Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


#Veiw for login
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


#view for Logout
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure authentication is required

    def post(self, request):
        try:
            # Extract the refresh token from the request data
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=400)

            # Blacklist the refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logged out successfully"}, status=200)

        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)


#view for Registrated for view
class RoleListView(APIView):
    """
    Endpoint to list all roles with their UUIDs.
    """
    # permission_classes = [IsAuthenticated]  # Optional: Only authenticated users can access
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)


#view for creating superAdmin 
class SuperAdminRegistrationAPIView(APIView):
    """
    API to register a new user and their SuperAdmin profile.
    """
    permission_classes = [IsSuperAdmin]

    def post(self, request, *args, **kwargs):
        serializer = SuperAdminCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SuperAdminListAPIView(ListAPIView):
    """
    API to list all SuperAdmins.
    """
    queryset = SuperAdmin.objects.all()
    serializer_class = SuperAdminSerializer
    permission_classes = [IsSuperAdmin]  # Restrict access to SuperAdmins only
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user','surname','first_name']
    

class SuperAdminDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    API to view, update, or delete a SuperAdmin profile.
    """
    queryset = SuperAdmin.objects.all()
    serializer_class = SuperAdminSerializer
    permission_classes = [IsSuperAdmin]  # Restrict access to SuperAdmins
    lookup_field = 'id'  # Use the 'id' field for lookup (UUID)

    def update(self, request, *args, **kwargs):
        """
        Handle updates to SuperAdmin profiles.
        """
        if 'id' in request.data:
            return Response({"error": "Cannot update the SuperAdmin ID."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion of SuperAdmin profiles. Restrict deletion to the same SuperAdmin or another SuperAdmin.
        """
        super_admin = self.get_object()

        # Prevent deletion of self (if desired)
        if request.user.super_admin == super_admin:
            return Response(
                {"error": "You cannot delete your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )

        super_admin.delete()
        return Response(
            {"message": f"SuperAdmin '{super_admin.first_name} {super_admin.surname}' has been deleted."},
            status=status.HTTP_204_NO_CONTENT
        )

#view for creating school
class SchoolCreateAPIView(APIView):
    """
    API to create a new School, restricted to authenticated users.
    """
    permission_classes = [IsSuperAdmin]  # Ensure only authenticated users can access this endpoint

    def post(self, request, *args, **kwargs):
        serializer = SchoolCreateSerializer(data=request.data, context={'request': request})  # Pass request to serializer
        if serializer.is_valid():
            serializer.save()  # `registered_by` will be set automatically
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#view to view the list of schools
class SchoolListAPIView(ListAPIView):
    """
    API to list all schools.
    """
    permission_classes = [IsSuperAdmin]  # Optional: Restrict access to authenticated users
    queryset = School.objects.all().order_by('school_name')
    serializer_class = SchoolListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['city', 'state', 'school_type', 'education_level']
    filter_backends = [SearchFilter]
    search_fields = ['school_name', 'short_name']

#views for both update and delete school
class SchoolDetailAPIView(RetrieveUpdateDestroyAPIView):
    """
    API to retrieve, update, or delete a school record.
    """
    queryset = School.objects.all()
    serializer_class = SchoolCreateSerializer
    permission_classes = [IsSuperAdmin]  # Default permission for authenticated users
    lookup_field = 'id'  # Using 'id' as the lookup field (UUID)

    def update(self, request, *args, **kwargs):
        """
        Handle updates for school records.
        """
        if 'id' in request.data:
            return Response({"error": "Cannot update the school ID."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Handle deletion of school records. Restrict deletion to SuperAdmins only.
        """
        if not request.user.is_authenticated or not hasattr(request.user, 'super_admin'):
            return Response(
                {"error": "You do not have permission to delete schools. Only SuperAdmins can perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )

        school = self.get_object()
        school_name = school.school_name
        school.delete()

        return Response(
            {"message": f"School '{school_name}' and all associated records have been deleted."},
            status=status.HTTP_204_NO_CONTENT
        )
# ========================================================================================================
class SubscriptionListView(generics.ListAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsSuperAdmin]

class SubscriptionDetailUpdateView(generics.RetrieveUpdateAPIView):
    """
    GET: View subscription detail with live student count, fee, and status.
    PATCH: Update amount_per_student and amount_paid only.
    """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsSuperAdmin]
    lookup_field = 'subscription_id'
    http_method_names = ['get', 'patch']

# ========================================================================================================
class ComplianceVerificationCreateView(generics.CreateAPIView):
    """
    Create a compliance verification record for a school.
    """
    queryset = ComplianceVerification.objects.all()
    serializer_class = ComplianceVerificationSerializer
    permission_classes = [IsSuperAdminOrSchoolAdmin]
    
    def perform_create(self, serializer):
        # Access the uploaded files from request.FILES
        accreditation_certificates = self.request.FILES.get('accreditation_certificates')
        proof_of_registration = self.request.FILES.get('proof_of_registration')

        # Save the instance with the uploaded files
        serializer.save(
            accreditation_certificates=accreditation_certificates,
            proof_of_registration=proof_of_registration
        )

class ComplianceVerificationListView(ListAPIView):
    """
    API view to list all compliance verification records.
    Supports filtering by school name, compliance status, and approval status.
    """
    queryset = ComplianceVerification.objects.all()
    serializer_class = ComplianceVerificationSerializer
    permission_classes = [IsSuperAdminOrSchoolAdmin]  # Ensure only authenticated users can access

    def get_queryset(self):
        """
        Optionally filters the queryset based on query parameters.
        """
        queryset = super().get_queryset()
        school_name = self.request.query_params.get('school_name', None)
        compliance = self.request.query_params.get('compliance', None)
        approved = self.request.query_params.get('approved', None)

        if school_name:
            queryset = queryset.filter(school__school_name__icontains=school_name)
        if compliance is not None:
            queryset = queryset.filter(compliance=compliance.lower() == 'true')
        if approved is not None:
            queryset = queryset.filter(approved=approved.lower() == 'true')

        return queryset


class ComplianceVerificationDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update compliance verification details for a school.
    """
    queryset = ComplianceVerification.objects.all()
    serializer_class = ComplianceVerificationSerializer
    lookup_field = 'school_id'  # Assuming you want to look up by school ID
    permission_classes = [IsSuperAdminOrSchoolAdmin]
    
# ================================Message module ========================================================================
# user_registration/views.py
class MessageCreateView(generics.CreateAPIView):
    """
    Send a new message.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sender = request.user
        recipient_ids = request.data.get('recipients', [])

        with transaction.atomic():
            if 'all_teachers' in request.data and request.data['all_teachers']:
                # Send to all teachers in the sender's school
                sender_school = self.get_user_school(sender)
                if sender_school:
                    teachers = Teacher.objects.filter(school=sender_school)
                    for teacher in teachers:
                        self.create_message(sender, teacher.user, serializer.validated_data)
                else:
                    return Response({'error': 'Sender school not found.'}, status=status.HTTP_400_BAD_REQUEST)

            elif 'class_level' in request.data and 'arm_name' in request.data:
                # Send to all students in the specified class and arm
                try:
                    classroom = Classroom.objects.get(class_level=request.data['class_level'], arm_name=request.data['arm_name'])
                    students = Student.objects.filter(classroom=classroom)
                    for student in students:
                        self.create_message(sender, student.user, serializer.validated_data)
                except Classroom.DoesNotExist:
                    return Response({'error': 'Class not found.'}, status=status.HTTP_400_BAD_REQUEST)

            else:
                # Send to individual recipients
                for recipient_id in recipient_ids:
                    try:
                        recipient = User.objects.get(pk=recipient_id)
                    except User.DoesNotExist:
                        return Response({'error': f'Recipient with ID {recipient_id} not found.'}, status=status.HTTP_400_BAD_REQUEST)

                    # Check if the sender is a superuser
                    if sender.is_superuser:
                        # Check if the recipient is a school admin
                        try:
                            SchoolAdmin.objects.get(user=recipient)
                        except SchoolAdmin.DoesNotExist:
                            return Response({'error': 'Superadmin can only send messages to school admins.'}, status=status.HTTP_403_FORBIDDEN)

                    # If the sender is not a superuser, check if they are in the same school as the recipient
                    else:
                        sender_school = self.get_user_school(sender)
                        recipient_school = self.get_user_school(recipient)

                        if not sender_school or not recipient_school or sender_school != recipient_school:
                            return Response({'error': 'You can only send messages to users in the same school.'}, status=status.HTTP_403_FORBIDDEN)

                    self.create_message(sender, recipient, serializer.validated_data)

        return Response({'message': 'Messages sent successfully.'}, status=status.HTTP_201_CREATED)

    def create_message(self, sender, recipient, validated_data):
        """
        Helper function to create and save a message.
        """
        Message.objects.create(
            sender=sender,
            recipient=recipient,
            subject=validated_data['subject'],
            content=validated_data['content'],
        )

    def get_user_school(self, user):
        try:
            user_role = UserRole.objects.get(user=user)
            if user_role.role.name == 'School Admin':
                return SchoolAdmin.objects.get(user=user).school
            elif user_role.role.name == 'Teacher':
                return Teacher.objects.get(user=user).school
            elif user_role.role.name == 'Student':
                return Student.objects.get(user=user).classroom.school
        except (UserRole.DoesNotExist, SchoolAdmin.DoesNotExist, Teacher.DoesNotExist, Student.DoesNotExist):
            pass
        return None
    
class MessageListView(generics.ListAPIView):
    """
    List messages for the current user.
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(recipient=user)  # Filter messages for the current user
    
# ============================================SchoolAdmin registration========================================================

class SchoolAdminCreateView(CreateAPIView):
    """
    Create a new SchoolAdmin.
    """
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminCreateSerializer
    permission_classes = [IsSuperAdmin]  # Add custom permissions if needed

class SchoolAdminListView(ListAPIView):
    """
    List all SchoolAdmins.
    """
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminListSerializer
    permission_classes = [IsSuperAdmin]

# from rest_framework.generics import RetrieveAPIView

class SchoolAdminDetailView(RetrieveAPIView):
    """
    Retrieve details of a specific SchoolAdmin.
    """
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminDetailSerializer
    lookup_field = 'schooladmin_id'  # Use UUID for lookup
    permission_classes = [IsSuperAdminOrSchoolAdmin]

class SchoolAdminUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific SchoolAdmin.
    """
    queryset = SchoolAdmin.objects.all()
    serializer_class = SchoolAdminUpdateSerializer
    lookup_field = 'schooladmin_id'
    permission_classes = [IsSuperAdminOrSchoolAdmin]



# ============================================student registration============================================================
# Views
class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentCreateSerializer
    permission_classes = [IsschoolAdmin]

    @swagger_auto_schema(
        request_body=StudentCreateSerializer,
        responses={
            201: openapi.Response('Student created successfully', StudentCreateSerializer),
            400: 'Bad Request',
        },
    )
    def perform_create(self, serializer):
        school = self.request.user.school_admin.school  # Automatically set the school
        serializer.save(school=school)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class StudentBulkCreateView(APIView):
    """
    Bulk register students from a CSV file (accessible by School Admin).
    Uses class_year_name and class_arm_name for readability.
    """
    parser_classes = [parsers.MultiPartParser]

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_csv(file_obj)

            required_fields = [
                'username', 'password', 'email', 'first_name', 'last_name', 'admission_number',
                'date_of_birth', 'gender', 'address', 'city', 'state', 'region', 'country',
                'admission_date', 'parent_first_name', 'parent_last_name',
                'parent_occupation', 'parent_contact_info', 'parent_emergency_contact',
                'parent_relationship', 'class_year_name', 'class_arm_name'
            ]

            missing_fields = set(required_fields) - set(df.columns)
            if missing_fields:
                return Response({'error': f'Missing fields in CSV: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

            school = request.user.school_admin.school
            student_role = Role.objects.get(name='Student')

            users, user_roles, students, student_classes = [], [], [], []
            errors = []

            for index, row in df.iterrows():
                try:
                    if not all(row[field] for field in required_fields):
                        errors.append({"row": index + 1, "error": "Missing required fields."})
                        continue

                    user = User(
                        username=row['username'],
                        email=row['email'],
                        first_name=row['first_name'],
                        last_name=row['last_name']
                    )
                    user.set_password(row['password'])
                    users.append(user)
                except Exception as e:
                    errors.append({"row": index + 1, "error": str(e)})

            if errors:
                return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            created_users = User.objects.bulk_create(users)

            for user, (_, row) in zip(created_users, df.iterrows()):
                user_role = UserRole(user=user, role=student_role)
                user_roles.append(user_role)

                student = Student(
                    user=user,
                    school=school,
                    admission_number=row['admission_number'],
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    date_of_birth=row['date_of_birth'],
                    gender=row['gender'],
                    address=row['address'],
                    city=row['city'],
                    state=row['state'],
                    region=row['region'],
                    country=row['country'],
                    admission_date=row['admission_date'],
                    parent_first_name=row['parent_first_name'],
                    parent_last_name=row['parent_last_name'],
                    parent_occupation=row['parent_occupation'],
                    parent_contact_info=row['parent_contact_info'],
                    parent_emergency_contact=row['parent_emergency_contact'],
                    parent_relationship=row['parent_relationship'],
                )
                students.append(student)

            created_students = []
            with transaction.atomic():
                UserRole.objects.bulk_create(user_roles)
                created_students = Student.objects.bulk_create(students)

                for student, (_, row) in zip(created_students, df.iterrows()):
                    class_year = ClassYear.objects.filter(year_name__iexact=row['class_year_name'], school=school).first()
                    class_arm = ClassDepartment.objects.filter(classes__arm_name__iexact=row['class_arm_name'], school=school).first()

                    if not class_year or not class_arm:
                        errors.append({"row": index + 1, "error": f"Invalid class year or arm: {row['class_year_name']}, {row['class_arm_name']}"})
                        continue

                    student_class = StudentClass(
                        student=student,
                        class_year=class_year,
                        class_arm=class_arm
                    )
                    student_classes.append(student_class)

                StudentClass.objects.bulk_create(student_classes)

            return Response({
                'message': 'Students registered successfully.',
                'errors': errors if errors else None
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': f'Error processing file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class GenerateRegistrationPinsView(APIView):
    """
    Generate multiple one-time pins for student self-registration.
    Accessible by School Admin.
    """
    permission_classes = [IsschoolAdmin]  # Ensure only School Admins can access

    def post(self, request, *args, **kwargs):
        # Get the authenticated School Admin's school
        school = request.user.school_admin.school  

        # Get the number of pins to generate
        num_pins = request.data.get('num_pins')

        # Validate num_pins input
        if not num_pins or not isinstance(num_pins, int) or num_pins <= 0:
            return Response({'error': 'Invalid number of pins.'}, status=400)

        pins = []
        with transaction.atomic():
            for _ in range(num_pins):
                otp = get_random_string(length=6, allowed_chars='0123456789')  # Generate a random 6-digit OTP
                pin = StudentRegistrationPin.objects.create(school=school, otp=otp)  # Create pin
                pins.append({
                    'pin_id': str(pin.pin_id),
                    'school_id': str(school.id),
                    'otp': otp
                })

        return Response({'message': 'Pins generated successfully.', 'pins': pins}, status=201)

class VerifyRegistrationPinView(APIView):
    """
    Verify OTP and School ID for student registration.
    """
    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        school_id = request.data.get('school_id')

        if not otp or not school_id:
            return Response({'error': 'OTP and school ID are required.'}, status=400)

        try:
            pin = StudentRegistrationPin.objects \
                    .get(otp=otp, school_id=school_id, is_used=False)
        except StudentRegistrationPin.DoesNotExist:
            return Response({'error': 'Invalid or used OTP.'}, status=400)

        temp_token = generate_temp_token(pin.pin_id, otp)

        school = School.objects.prefetch_related("classes", "class_years").get(id=school_id)

        # Quick dictionary serialization (or you can use serializers if you want more control)
        class_years_data = []
        for class_year in school.class_years.all():
            class_arms_data = []
            for _class in school.classes.filter(class_year=class_year):
                class_arms_data.append({
                    "class_id": _class.class_id,
                    "arm_name": _class.arm_name
                })

            class_years_data.append({
                "id": str(class_year.class_year_id),
                "name": class_year.class_name,
                "class_arms": class_arms_data
            })


        # return Response({'message': 'Verification successful.', 'temp_token': temp_token}, status=200)
        return Response({
            'message': 'Verification successful.',
            'temp_token': temp_token,
            'class_years': class_years_data,
        }, status=200)

# from school_config.serializers import ClassYearSerializer, ClassDepartmentSerializer  # if you decide to use serializers


class ListRegistrationPinsView(generics.ListAPIView):
    """
    Retrieve all generated registration pins for a school.
    Accessible only by School Admins.
    """
    serializer_class = RegistrationPinSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        return StudentRegistrationPin.objects.filter(school=self.request.user.school_admin.school)

    @swagger_auto_schema(
        responses={
            200: openapi.Response("List of registration pins"),
            403: "User does not have permission to view registration pins."
        }
    )
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({"message": "List of registration pins.", "pins": serializer.data}, status=status.HTTP_200_OK)


class StudentSelfRegistrationView(generics.CreateAPIView):
    """
    Self-registration for students after OTP verification.
    Automatically assigns the student to class_year and class_arm.
    """
    serializer_class = StudentCreateSerializer

    def post(self, request, *args, **kwargs):
        temp_token = request.data.get('temp_token')
        class_year_name = request.data.get('class_year_name')
        class_arm_name = request.data.get('class_arm_name')

        if not temp_token:
            return Response({'error': 'Temporary token is required.'}, status=400)

        is_valid, pin = validate_temp_token(temp_token)
        if not is_valid:
            return Response({'error': 'Invalid or expired temporary token.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Mark OTP as used
        pin.is_used = True
        pin.save()

        # Create student record
        student = serializer.save(school=pin.school)

        # Assign class using provided class_year_name and class_arm_name
        if not class_year_name or not class_arm_name:
            return Response({'error': 'class_year_name and class_arm_name are required.'}, status=400)

        # class_year = ClassYear.objects.filter(year_name__iexact=class_year_name, school=pin.school).first()
        # class_arm = Class.objects.filter(classes__arm_name__iexact=class_arm_name, school=pin.school).first()

        class_year = ClassYear.objects.filter(class_name__iexact=class_year_name, school=pin.school).first()
        class_arm = Class.objects.filter(arm_name__iexact=class_arm_name, school=pin.school, class_year=class_year).first()


        if not class_year or not class_arm:
            return Response({'error': 'Invalid class_year_name or class_arm_name.'}, status=400)

        StudentClass.objects.create(
            student=student,
            class_year=class_year,
            class_arm=class_arm
        )

        return Response(serializer.data, status=201)


class StudentUpdateView(generics.RetrieveUpdateAPIView):
    """
    Allows a student to view and update their own profile, including class assignment.
    """
    queryset = Student.objects.all()
    serializer_class = StudentUpdateSerializer
    permission_classes = [IsschoolAdmin | ISstudent]

    def get_object(self):
        # Ensure the student can only access their own record
        return self.queryset.get(user=self.request.user)


class StudentListView(generics.ListAPIView):
    """
    Allows School Admin to list all students in their school, with class info.
    """
    queryset = Student.objects.all()
    serializer_class = StudentListSerializer
    permission_classes = [IsschoolAdmin]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['first_name', 'middle_name', 'last_name', 'gender']
    search_fields = ['city', 'region', 'country']

    def get_queryset(self):
        # Return only students in the School Admin's school
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return self.queryset.none()
        return self.queryset.filter(school=self.request.user.school_admin.school)


class DeleteMultipleStudentsView(APIView):
    """
    API to delete multiple students by their IDs.
    Accessible by School Admins only.
    """
    permission_classes = [IsschoolAdmin]

    def delete(self, request, *args, **kwargs):
        student_ids = request.data.get('student_ids', [])
        if not student_ids or not isinstance(student_ids, list):
            return Response({"error": "A list of student IDs is required."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = Student.objects.filter(student_id__in=student_ids).delete()[0]
        return Response({"message": f"{deleted_count} student(s) deleted successfully."}, status=status.HTTP_200_OK)


class StudentDetailView(RetrieveAPIView):
    """
    API to retrieve a single student's details, including class assignment.
    """
    queryset = Student.objects.all()
    serializer_class = StudentDetailSerializer
    permission_classes = [IsschoolAdmin | ISstudent]
    lookup_field = 'pk'


# ========================================================================================================
class TeacherCreateView(generics.CreateAPIView):
    """
    Create a new teacher record.
    Accessible by School Admin.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherCreateSerializer
    permission_classes = [IsschoolAdmin]

    def perform_create(self, serializer):
        school = self.request.user.school_admin.school  # Automatically set the school
        serializer.save(school=school)


class TeacherBulkCreateView(APIView):
    """
    Bulk register teachers from a CSV file (accessible by School Admin).
    - Optimized for speed using bulk inserts.
    - Ensures data validation before inserting any records.
    - Prevents user creation if teacher data has errors.
    """
    permission_classes = [IsschoolAdmin]
    parser_classes = [parsers.MultiPartParser]
    serializer_class = TeacherCreateSerializer 


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'file', openapi.IN_FORM, description="CSV file containing teacher data", type=openapi.TYPE_FILE
            )
        ],
        responses={
            201: openapi.Response('Teachers registered successfully'),
            400: openapi.Response('Bad Request'),
        }
    )
    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')

        if not file_obj:
            print(f"Error: No file detected in request.FILES")  # Debugging
            print(f"Available keys in request.FILES: {request.FILES.keys()}")  # Debugging
            return Response({'error': 'No file uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read CSV file using pandas for speed
            df = pd.read_csv(file_obj)

            # Define required fields
            required_fields = [
                'username', 'password', 'email', 'first_name', 'last_name', 'date_of_birth', 'gender',
                'address', 'city', 'state', 'region', 'country', 'date_hire', 'qualification', 'specialization'
            ]
            
            # Check for missing fields
            missing_fields = set(required_fields) - set(df.columns)
            if missing_fields:
                return Response({'error': f'Missing fields in CSV: {", ".join(missing_fields)}'}, status=status.HTTP_400_BAD_REQUEST)

            school = request.user.school_admin.school  # Fetch once
            role = Role.objects.get(name='Teacher')  # Fetch once

            # Lists to collect valid records
            users, user_roles, teachers = [], [], []
            errors = []

            for index, row in df.iterrows():
                try:
                    # Validate required fields per teacher
                    if not all(row[field] for field in required_fields):
                        errors.append({"row": index + 1, "error": "Missing required fields."})
                        continue

                    user = User(
                        username=row['username'],
                        email=row['email'],
                    )
                    user.set_password(row['password'])  # Hash password
                    users.append(user)
                    
                except Exception as e:
                    errors.append({"row": index + 1, "error": str(e)})

            # If any errors were found, return them before creating users
            if errors:
                return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

            # Bulk create users
            created_users = User.objects.bulk_create(users)

            # Prepare user roles and teachers
            for user, (_, row) in zip(created_users, df.iterrows()):
                user_role = UserRole(user=user, role=role)
                user_roles.append(user_role)

                teacher = Teacher(
                    user=user,
                    school=school,
                    first_name=row['first_name'],
                    middle_name=row.get('middle_name', ''),  # Optional field
                    last_name=row['last_name'],
                    date_of_birth=row['date_of_birth'],
                    gender=row['gender'],
                    address=row['address'],
                    city=row['city'],
                    state=row['state'],
                    region=row['region'],
                    country=row['country'],
                    date_hire=row['date_hire'],
                    qualification=row['qualification'],
                    specialization=row['specialization'],
                    profile_picture_path=row.get('profile_picture_path', None),
                    cv=row.get('cv', None),
                )
                teachers.append(teacher)

            # Bulk create user roles and teachers
            with transaction.atomic():
                UserRole.objects.bulk_create(user_roles)
                Teacher.objects.bulk_create(teachers)

            return Response({'message': 'Teachers registered successfully.'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging
            return Response({'error': f'Error processing file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class TeacherSelfRegistrationView(generics.CreateAPIView):
    """
    Self-registration for students after OTP verification.
    """
    serializer_class = TeacherCreateSerializer

    def post(self, request, *args, **kwargs):
        temp_token = request.data.get('temp_token')

        if not temp_token:
            return Response({'error': 'Temporary token is required.'}, status=400)

        is_valid, pin = validate_temp_token(temp_token)
        if not is_valid:
            return Response({'error': 'Invalid or expired temporary token.'}, status=400)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Mark OTP as used
        pin.is_used = True
        pin.save()

        # Create student record
        serializer.save(school=pin.school)
        return Response(serializer.data, status=201)


class TeacherUpdateView(generics.UpdateAPIView):
    """
    Update a teacher's profile.
    Accessible by the teacher themselves.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherUpdateSerializer
    permission_classes = [ISteacher]

    def get_queryset(self):
        return Teacher.objects.filter(user=self.request.user)


class TeacherListView(generics.ListAPIView):
    """
    List all teachers in a school.
    Accessible by School Admin.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherListSerializer
    permission_classes = [IsschoolAdmin|ISteacher]
    # pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['first_name', 'middle_name', 'last_name', 'gender']
    filter_backends = [SearchFilter]
    search_fields = ['city', 'region','country']

    def get_queryset(self):
        return Teacher.objects.filter(school=self.request.user.school_admin.school)


class DeleteMultipleTeachersView(APIView):
    """
    API to delete multiple teachers by their IDs.
    Accessible by School Admins only.
    """
    permission_classes = [IsschoolAdmin]

    def delete(self, request, *args, **kwargs):
        teacher_ids = request.data.get('teacher_ids', [])
        if not teacher_ids or not isinstance(teacher_ids, list):
            return Response({"error": "A list of teacher IDs is required."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = Teacher.objects.filter(teacher_id__in=teacher_ids).delete()[0]
        return Response({"message": f"{deleted_count} teacher(s) deleted successfully."}, status=status.HTTP_200_OK)


class TeacherDetailView(RetrieveAPIView):
    """
    API to retrieve a single teacher's details.
    """
    queryset = Teacher.objects.all()
    serializer_class = TeacherDetailSerializer
    permission_classes = [IsschoolAdmin|ISteacher]  # Only School Admins can access
    lookup_field = 'pk'  # Allows retrieval by primary key


