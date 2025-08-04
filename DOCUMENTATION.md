# School Management System - Comprehensive Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Core Applications](#core-applications)
4. [Database Models](#database-models)
5. [API Endpoints](#api-endpoints)
6. [Authentication & Authorization](#authentication--authorization)
7. [Key Features & Workflows](#key-features--workflows)
8. [Third-Party Integrations](#third-party-integrations)
9. [Deployment Configuration](#deployment-configuration)
10. [Development Guidelines](#development-guidelines)

## System Overview

The School Management System is a comprehensive Django REST API application designed to manage all aspects of school operations. It provides a complete solution for academic institutions to handle student enrollment, teacher management, academic records, timetable generation, result processing, and administrative tasks.

### Purpose
The system serves as a centralized platform for:
- Multi-school management with subscription-based access
- Student and teacher lifecycle management
- Academic year, term, and class structure management
- Subject registration and assignment workflows
- Automated timetable generation using ACO algorithms
- Comprehensive result processing and grade calculation
- Notification and communication systems
- Statistical reporting and analytics

### Target Users
- **Super Admins**: Platform administrators managing multiple schools
- **School Admins**: School-level administrators managing their institution
- **Teachers**: Faculty members managing classes and assessments
- **Students**: Learners accessing their academic information

## Architecture & Technology Stack

### Backend Framework
- **Django 5.1.4**: Main web framework
- **Django REST Framework 3.15.2**: API development
- **PostgreSQL/SQLite**: Database backend

### Authentication & Security
- **Django Simple JWT 5.3.1**: Token-based authentication
- **Django CORS Headers 4.7.0**: Cross-origin resource sharing
- **Custom permission classes**: Role-based access control

### API Documentation
- **drf-yasg 1.21.8**: Swagger/OpenAPI documentation
- **Django Filters 24.3**: Advanced filtering capabilities

### File Handling & Storage
- **Pillow 11.0.0**: Image processing
- **WhiteNoise 6.9.0**: Static file serving
- **Django FileSystemStorage**: Media file management

### Data Processing
- **Pandas 2.2.3**: Data analysis and processing
- **NumPy 2.2.1**: Numerical computations

### Email & Notifications
- **Django Email Backend**: SMTP email integration

## Core Applications

### 1. user_registration
**Primary Purpose**: Core user management, school setup, and foundational data models

**Key Responsibilities**:
- User authentication and role management
- School registration and compliance verification
- Student and teacher profile management
- Academic structure (years, terms, classes, subjects)
- Subscription management and billing
- Pin-based registration systems

### 2. school_config
**Primary Purpose**: School-specific configuration and academic setup

**Key Responsibilities**:
- Academic year and term management
- Class and department configuration
- Subject assignment and teacher allocation
- Student class assignments
- Subject registration controls

### 3. result
**Primary Purpose**: Academic assessment and result processing

**Key Responsibilities**:
- Assessment category configuration
- Score recording and calculation
- Grade assignment and result generation
- Annual result computation with weighted averages
- AI-powered teacher comment generation
- Result visibility controls

### 4. timetable
**Primary Purpose**: Automated timetable generation and management

**Key Responsibilities**:
- Constraint-based timetable generation using ACO algorithms
- Teacher availability management
- Subject period limit enforcement
- Class and teacher timetable distribution

### 5. notification
**Primary Purpose**: Communication and notification system

**Key Responsibilities**:
- Role-based notification delivery
- Message broadcasting to specific user groups
- Notification history and read status tracking

### 6. Allstat
**Primary Purpose**: Statistical reporting and analytics

**Key Responsibilities**:
- Student and teacher demographic statistics
- Gender-based reporting
- School-wide analytics dashboard

## Database Models

### Core User Management Models

#### Role
- Defines system roles (Super Admin, School Admin, Teacher, Student)
- UUID primary key for security
- Hierarchical permission structure

#### User (Django Built-in)
- Standard Django user model
- Extended through one-to-one relationships

#### UserRole
- Many-to-many relationship between users and roles
- Supports multiple role assignments

#### SuperAdmin
- System-wide access through permissions, not model relationships
- Can view and manage any school via the API endpoints
- Platform administration (managing the entire system)
- No ownership model - they manage through elevated permissions

#### School
- Central entity representing educational institutions
- Contains school profile, contact information, and configuration
- Supports logo upload and compliance documentation
- Links to subscription and billing information

#### SchoolAdmin
- School-level administrators
- Manages single school operations
- Limited to their assigned school's data

### Academic Structure Models

#### Year
- Represents academic years
- Contains start/end dates and active status
- Only one active year per school at a time

#### Term
- Academic terms within years (e.g., First Term, Second Term)
- Linked to specific years and schools
- Controls term-based operations

#### ClassYear
- Grade levels (e.g., Grade 1, Grade 2, JSS 1)
- Foundation for organizing students

#### Class
- Specific class arms (e.g., Grade 1A, Grade 1B)
- Links students to specific class sections

#### Department
- Academic departments (Science, Arts, Commercial)
- Groups subjects and classes by academic focus

#### Subject
- Individual subjects offered by schools
- Can be assigned to multiple classes and departments

### User Profile Models

#### Student
- Comprehensive student profiles
- Academic and personal information
- Parent/guardian details
- Admission tracking and status management
- Profile picture support

#### Teacher
- Teacher profiles with professional information
- Qualification and specialization tracking
- CV and document storage
- Employment history and status

#### StudentClass
- Links students to their current class assignments
- Supports class changes and academic progression

#### ClassTeacher
- Assigns teachers as class coordinators
- Manages pastoral care responsibilities

### Subject Assignment Models

#### SubjectClass
- Links subjects to departments within schools
- Enables department-based subject organization

#### ClassDepartment
- Associates classes with academic departments
- Supports stream-based education systems

#### TeacherAssignment
- Maps teachers to specific subjects and classes
- Manages teaching loads and assignments

#### StudentSubjectRegistration
- Records student subject selections
- Supports approval workflows
- Maintains historical class information
- Term-based registration system

### Assessment & Results Models

#### AssessmentCategory
- Defines assessment types (Quiz, Test, Assignment)
- Configures maximum scores and frequency

#### ScorePerAssessmentInstance
- Records individual assessment scores
- Links to specific assessment instances

#### ScoreObtainedPerAssessment
- Aggregated scores per assessment category
- Calculated totals for each assessment type

#### ExamScore
- Final examination scores
- Separate from continuous assessments

#### ContinuousAssessment
- Aggregated CA scores from all assessments
- Calculated based on school configuration

#### Result
- Complete term results combining CA and exam scores
- Grade assignment and remarks
- Automatic calculation based on school configuration

#### AnnualResult
- Year-end results combining all terms
- Weighted average calculations
- Annual grade and remarks assignment

#### GradingSystem
- School-specific grading scales
- Customizable grade boundaries and remarks

#### ResultConfiguration
- School-wide result calculation settings
- CA/Exam score distributions
- Pass mark configuration

#### ClassTeacherComment
- Term-based teacher comments for students
- AI-assisted comment generation
- Pastoral care documentation

### Timetable Models

#### Day
- School days configuration
- Supports custom school week structures

#### Period
- Time periods for timetable slots
- Start and end time definitions

#### SubjectPeriodLimit
- Subject-specific timetable constraints
- Weekly period allocations
- Double period configurations

#### Constraint
- Global and class-specific timetable restrictions
- Break times and special period management

#### Timetable
- Generated timetable container
- Links to class and teacher schedules

#### ClassTimetable & TeacherTimetable
- Specific timetables for classes and teachers
- JSON-based schedule storage

### Subscription & Billing Models

#### Subscription
- School subscription management
- Student-based billing calculations
- Active status tracking with dynamic calculations

#### ComplianceVerification
- School registration compliance
- Document storage and approval workflow

### Notification & Communication Models

#### Message
- Direct user-to-user messaging
- Read status tracking

#### Notification
- System-wide notifications
- Role-based targeting (Teachers, Students, Everyone)
- Notification type categorization

### Administrative Models

#### StudentRegistrationPin
- One-time pins for student self-registration
- School-specific pin generation
- Usage tracking and validation

#### SubjectRegistrationControl
- Controls student subject registration periods
- Date-based registration windows

#### AttendancePolicy
- School attendance requirements
- Minimum attendance thresholds

#### Attendance & AttendanceFlag
- Daily attendance recording
- Attendance percentage monitoring
- Automatic flagging for poor attendance

#### Fee Management (FeeCategory, Fee)
- Class-based fee structures
- Individual student fee tracking

## API Endpoints

### Authentication Endpoints
```
POST /api/login/ - User authentication
POST /api/login/refresh/ - Token refresh
POST /api/logout/ - User logout
GET /api/roles/ - List available roles
```

### User Management Endpoints
```
POST /api/superadmins/create/ - Create super admin
GET /api/superadmins/ - List super admins
GET /api/superadmins/{id}/ - Super admin details

GET /api/schools/ - List schools
POST /api/schools/create/ - Create school
GET /api/schools/{id}/ - School details

GET /api/schools/subscriptions/ - List subscriptions
PUT /api/schools/subscriptions/{id}/ - Update subscription
```

### Academic Management Endpoints
```
GET /api/years/ - List academic years
POST /api/years/ - Create academic year
PUT /api/years/{id}/ - Update academic year

GET /api/terms/ - List terms
POST /api/terms/ - Create term

GET /api/classes/ - List classes
POST /api/classes/ - Create class

GET /api/subjects/ - List subjects
POST /api/subjects/ - Create subject
```

### Student & Teacher Management
```
GET /api/students/ - List students
POST /api/students/create/ - Create student
POST /api/students/bulk-create/ - Bulk create students
PUT /api/students/{id}/ - Update student

GET /api/teachers/ - List teachers
POST /api/teachers/create/ - Create teacher
POST /api/teachers/bulk-create/ - Bulk create teachers
```

### Result Management Endpoints
```
GET /api/results/assessment-categories/ - List assessment categories
POST /api/results/assessment-categories/ - Create assessment category

GET /api/results/scores/ - List scores
POST /api/results/scores/ - Record scores

GET /api/results/term-results/ - Get term results
GET /api/results/annual-results/ - Get annual results
```

### Timetable Endpoints
```
POST /api/timetable/generate/ - Generate timetable
GET /api/timetable/class/ - Get class timetable
GET /api/timetable/teacher/ - Get teacher timetable
```

### Notification Endpoints
```
GET /api/notifications/ - List notifications
POST /api/notifications/ - Create notification
GET /api/notifications/recent/ - Recent notifications
```

## Authentication & Authorization

### JWT Token Authentication
- Access tokens valid for 1 day
- Refresh tokens valid for 1 day
- Automatic token refresh capability

### Role-Based Permissions

#### IsSuperAdmin
- Full system access
- Multi-school management
- System configuration

#### IsSchoolAdmin
- Single school management
- Academic configuration
- User management within school

#### IsTeacher
- Limited to assigned classes and subjects
- Score entry and class management
- Student information access

#### IsStudent
- Read-only access to personal information
- Academic records and timetables
- Notification access

### Custom Permissions
- **HasValidPinAndSchoolId**: Pin-based registration
- **IsClassTeacher**: Enhanced teacher permissions
- **SchoolAdminOrIsClassTeacherOrISstudent**: Layered access control

## Key Features & Workflows

### 1. School Registration & Setup Workflow
1. Super Admin creates school record
2. Compliance documentation upload
3. School Admin account creation
4. Subscription configuration
5. Academic structure setup (years, terms, classes)
6. Subject and department configuration

### 2. Student Enrollment Workflow
1. Admin generates registration pins
2. Student self-registration using pin
3. Academic placement and class assignment
4. Subject registration (when open)
5. Parent information recording

### 3. Teacher Management Workflow
1. Teacher profile creation
2. Subject and class assignment
3. Class teacher designation
4. Timetable allocation

### 4. Academic Assessment Workflow
1. Assessment category configuration
2. Score recording per assessment instance
3. Continuous assessment calculation
4. Exam score entry
5. Term result computation
6. Grade assignment and teacher comments
7. Annual result compilation

### 5. Timetable Generation Workflow
1. Configure school days and periods
2. Set subject period limits
3. Define constraints (breaks, fellowship)
4. Teacher availability input
5. ACO algorithm execution
6. Timetable distribution to classes and teachers

### 6. Result Processing Workflow
1. Score aggregation from assessments
2. CA total calculation
3. Exam score integration
4. Grade calculation using school grading system
5. Teacher comment generation (AI-assisted)
6. Result publication with visibility controls

## Third-Party Integrations

### Swagger API Documentation
- Complete API documentation at `/swagger/`
- Interactive API testing interface
- Schema validation and examples

### AI Comment Generation
- Placeholder for transformer-based comment generation
- Student skill assessment integration
- Gender-aware pronoun usage

### Email Integration
- SMTP configuration for notifications
- Password reset functionality
- System notifications

### File Upload & Storage
- Image processing for profiles and logos
- Document storage for compliance
- CV and certificate management

## Deployment Configuration

### Production Settings
- **ALLOWED_HOSTS**: Configured for PythonAnywhere deployment
- **DEBUG**: Set to False for production
- **STATIC_FILES**: WhiteNoise middleware for static file serving
- **MEDIA_FILES**: FileSystemStorage configuration

### Database Configuration
- SQLite for development
- PostgreSQL support for production
- Migration management

### Security Features
- CSRF protection enabled
- CORS headers configured
- Secret key management
- Password validation rules

## Development Guidelines

### Project Structure
```
School_management/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── school_managementApp/          # Main project settings
├── user_registration/             # Core user management
├── school_config/                 # Academic configuration
├── result/                        # Assessment and results
├── timetable/                     # Timetable generation
├── notification/                  # Communication system
├── Allstat/                       # Statistics and analytics
└── media/                         # Uploaded files
```

### Code Organization
- **Models**: Database schema in `models.py`
- **Views**: API logic in `views.py`
- **Serializers**: Data serialization in `serializers.py`
- **Permissions**: Custom permissions in `permissions.py`
- **URLs**: Endpoint routing in `urls.py`
- **Utils**: Helper functions in `utils.py`

### Best Practices
1. Use UUID primary keys for security
2. Implement proper permission classes
3. Validate data using serializers
4. Handle errors gracefully
5. Use transactions for data integrity
6. Implement pagination for large datasets
7. Add proper logging and monitoring

### Testing Considerations
- Unit tests for models and views
- API endpoint testing
- Permission testing
- Data validation testing
- Performance testing for large datasets

### Scaling Considerations
- Database indexing for large schools
- Caching for frequently accessed data
- Background task processing for bulk operations
- File storage optimization
- API rate limiting

## Future Enhancements

### Planned Features
1. Mobile application support
2. Parent portal integration
3. Financial management module
4. Library management system
5. Transport management
6. Hostel management
7. Advanced analytics and reporting
8. Integration with external examination bodies

### Technical Improvements
1. Real-time notifications using WebSockets
2. Advanced caching strategies
3. Microservices architecture
4. Container deployment
5. Automated testing pipeline
6. Performance monitoring
7. Security auditing

This documentation provides a comprehensive overview of the School Management System, enabling Django developers to understand, contribute to, and extend the system effectively.
