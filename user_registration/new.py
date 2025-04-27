class VerifyRegistrationPinView(APIView):
    """
    Verify OTP and School ID for student registration.
    After successful verification, return temp_token, class_years, and class_arms.
    """
    def post(self, request, *args, **kwargs):
        otp = request.data.get('otp')
        school_id = request.data.get('school_id')

        if not otp or not school_id:
            return Response({'error': 'OTP and school ID are required.'}, status=400)

        try:
            pin = StudentRegistrationPin.objects.get(otp=otp, school_id=school_id, is_used=False)
        except StudentRegistrationPin.DoesNotExist:
            return Response({'error': 'Invalid or used OTP.'}, status=400)

        # Generate temp_token
        temp_token = generate_temp_token(pin.pin_id, otp)

        # Fetch available class years and class arms for the school
        class_years = ClassYear.objects.filter(school=pin.school)
        class_arms = ClassDepartment.objects.filter(school=pin.school)

        # Quick dictionary serialization (or you can use serializers if you want more control)
        class_years_data = [{"id": str(cy.class_year_id), "name": cy.name} for cy in class_years]
        class_arms_data = [{"id": str(ca.subject_class_id), "name": ca.name} for ca in class_arms]

        return Response({
            'message': 'Verification successful.',
            'temp_token': temp_token,
            'class_years': class_years_data,
            'class_arms': class_arms_data
        }, status=200)
