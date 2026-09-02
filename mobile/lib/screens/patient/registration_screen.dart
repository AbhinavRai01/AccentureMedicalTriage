import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../config.dart';

class RegistrationScreen extends StatefulWidget {
  final String? accountId;
  const RegistrationScreen({super.key, this.accountId});

  @override
  State<RegistrationScreen> createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  int _currentStep = 0;
  final _formKeys = [
    GlobalKey<FormState>(),
    GlobalKey<FormState>(),
    GlobalKey<FormState>(),
    GlobalKey<FormState>(),
  ];

  final Map<String, dynamic> _formData = {};
  bool _isSubmitting = false;

  void _submitForm() async {
    if (widget.accountId != null) {
      _formData['account_id'] = widget.accountId;
    }
    setState(() => _isSubmitting = true);
    try {
      final res = await http.post(
        Uri.parse('${AppConfig.apiBaseUrl}/api/patient/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(_formData),
      );

      if (res.statusCode == 201) {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Registration Successful!')));
        Navigator.pop(context);
      } else {
        throw Exception('Registration failed: ${res.body}');
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        title: const Row(
          children: [
            Icon(Icons.medical_services_outlined, color: Color(0xFF006B4D)),
            SizedBox(width: 8),
            Text('Registration', style: TextStyle(color: Color(0xFF1A1A1A), fontWeight: FontWeight.bold)),
          ],
        ),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF1A1A1A)),
      ),
      body: _isSubmitting 
          ? const Center(child: CircularProgressIndicator(color: Color(0xFF006B4D)))
          : Theme(
              data: Theme.of(context).copyWith(
                colorScheme: const ColorScheme.light(primary: Color(0xFF006B4D)),
              ),
              child: Stepper(
                type: StepperType.vertical,
                currentStep: _currentStep,
                elevation: 0,
                physics: const ClampingScrollPhysics(),
                controlsBuilder: (context, details) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 24.0),
                    child: Column(
                      children: [
                        ElevatedButton(
                          onPressed: details.onStepContinue,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF006B4D),
                            minimumSize: const Size.fromHeight(56),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          ),
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(_currentStep == 3 ? 'Submit' : 'Continue', style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                              const SizedBox(width: 8),
                              const Icon(Icons.arrow_forward, color: Colors.white, size: 20),
                            ],
                          ),
                        ),
                        if (_currentStep > 0)
                          TextButton(
                            onPressed: details.onStepCancel,
                            child: const Text('Cancel', style: TextStyle(color: Color(0xFF006B4D))),
                          ),
                      ],
                    ),
                  );
                },
                onStepContinue: () {
                  if (_currentStep < 3) {
                    if (_formKeys[_currentStep].currentState!.validate()) {
                      _formKeys[_currentStep].currentState!.save();
                      setState(() => _currentStep += 1);
                    }
                  } else {
                    if (_formKeys[_currentStep].currentState!.validate()) {
                      _formKeys[_currentStep].currentState!.save();
                      _submitForm();
                    }
                  }
                },
                onStepCancel: () {
                  if (_currentStep > 0) {
                    setState(() => _currentStep -= 1);
                  }
                },
                steps: [
                  _buildStep(
                    0, 
                    'Personal Details', 
                    'Please provide your basic information.',
                    [
                      _buildTextField('Full Name', 'e.g. Jane Doe', (v) => _formData['name'] = v, required: true),
                      _buildTextField('Date of Birth', 'YYYY-MM-DD', (v) => _formData['dob'] = v, icon: Icons.calendar_today),
                      _buildTextField('Biological Sex', 'Select option...', (v) => _formData['gender'] = v),
                      _buildTextField('Phone Number', '(555) 000-0000', (v) => _formData['phone'] = v),
                      _buildTextField('Email Address', 'jane.doe@example.com', (v) => _formData['email'] = v),
                      _buildTextField('Home Address', '123 Wellness Way...', (v) => _formData['address'] = v),
                      const SizedBox(height: 16),
                      const Row(
                        children: [
                          Icon(Icons.emergency, color: Color(0xFFBE123C)),
                          SizedBox(width: 8),
                          Text('Emergency Contact', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const SizedBox(height: 16),
                      _buildTextField('Contact Name', 'Full Name', (v) => _formData['emergency_contact_name'] = v),
                      _buildTextField('Contact Phone', '(555) 000-0000', (v) => _formData['emergency_contact_phone'] = v),
                    ]
                  ),
                  _buildStep(
                    1, 
                    'Insurance & Visit', 
                    'Coverage and reason for visit.',
                    [
                      _buildTextField('Insurance Provider', 'e.g. Blue Cross', (v) => _formData['insurance_provider'] = v),
                      _buildTextField('Policy Number', 'e.g. ABC123456789', (v) => _formData['insurance_policy_number'] = v),
                      _buildTextField('Primary Reason for Visit', 'e.g. Chest pain', (v) => _formData['reason_for_visit'] = v),
                      _buildTextField('How long have you had this issue?', 'e.g. 2 days', (v) => _formData['duration_of_issue'] = v),
                    ]
                  ),
                  _buildStep(
                    2, 
                    'Medical History', 
                    'Existing conditions and allergies.',
                    [
                      _buildTextField('Current Conditions', 'e.g. Diabetes, Hypertension', (v) => _formData['medical_conditions'] = [v]),
                      _buildTextField('Medications', 'e.g. Lisinopril', (v) => _formData['medications_list'] = v),
                      _buildTextField('Allergies', 'e.g. Penicillin', (v) => _formData['allergies_list'] = v),
                      _buildTextField('Past Surgeries', 'e.g. Appendectomy', (v) => _formData['surgeries_list'] = v),
                    ]
                  ),
                  _buildStep(
                    3, 
                    'Lifestyle & Pharmacy', 
                    'Additional health factors.',
                    [
                      _buildTextField('Tobacco Use (Yes/No)', 'e.g. No', (v) => _formData['tobacco_use'] = v),
                      _buildTextField('Occupation', 'e.g. Teacher', (v) => _formData['occupation'] = v),
                      _buildTextField('Preferred Pharmacy Name', 'e.g. CVS', (v) => _formData['pharmacy_name'] = v),
                      const SizedBox(height: 16),
                      const Text('By submitting, I confirm the information is accurate.', style: TextStyle(color: Color(0xFF6B7280))),
                    ]
                  ),
                ],
              ),
            ),
    );
  }

  Step _buildStep(int index, String title, String subtitle, List<Widget> fields) {
    return Step(
      title: Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1A1A1A))),
      subtitle: Text(subtitle, style: const TextStyle(color: Color(0xFF6B7280))),
      isActive: _currentStep >= index,
      state: _currentStep > index ? StepState.complete : StepState.indexed,
      content: Container(
        margin: const EdgeInsets.only(top: 16),
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Form(
          key: _formKeys[index],
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: fields,
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(String label, String hint, Function(String?) onSaved, {bool required = false, IconData? icon}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w600, color: Color(0xFF1A1A1A))),
          const SizedBox(height: 8),
          TextFormField(
            decoration: InputDecoration(
              hintText: hint,
              hintStyle: const TextStyle(color: Color(0xFF9CA3AF)),
              filled: true,
              fillColor: const Color(0xFFF3F4F6),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
              suffixIcon: icon != null ? Icon(icon, color: const Color(0xFF4A4A4A)) : null,
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
            ),
            validator: required ? (v) => v!.isEmpty ? 'Required' : null : null,
            onSaved: onSaved,
          ),
        ],
      ),
    );
  }
}
