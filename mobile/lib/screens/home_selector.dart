import 'package:flutter/material.dart';
import 'patient/patient_landing.dart';
import 'clinical/nurse_portal.dart';
import 'clinical/doctor_portal.dart';

class HomeSelectorScreen extends StatelessWidget {
  const HomeSelectorScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.medical_services_outlined, size: 64, color: Color(0xFF006B4D)),
              const SizedBox(height: 16),
              const Text(
                'Triage System',
                style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: Color(0xFF1A1A1A)),
              ),
              const SizedBox(height: 8),
              const Text(
                'Select your portal to securely access\nthe clinical network.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 16, color: Color(0xFF4A4A4A)),
              ),
              const SizedBox(height: 48),
              
              // Patient Portal Button
              InkWell(
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PatientLandingScreen())),
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 24),
                  decoration: BoxDecoration(
                    color: const Color(0xFF006B4D),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.family_restroom, color: Colors.white, size: 32),
                      const SizedBox(width: 16),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('PORTAL', style: TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                            Text('Patient & Family', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w600)),
                          ],
                        ),
                      ),
                      const Icon(Icons.arrow_forward, color: Colors.white),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 32),
              Row(
                children: [
                  const Expanded(child: Divider(color: Color(0xFFD1D5DB))),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16.0),
                    child: Text('CLINICAL STAFF', style: TextStyle(color: Color(0xFF6B7280), fontSize: 12, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
                  ),
                  const Expanded(child: Divider(color: Color(0xFFD1D5DB))),
                ],
              ),
              const SizedBox(height: 32),
              
              // Nurse Portal
              InkWell(
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NursePortalScreen())),
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE5E7EB)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(color: const Color(0xFFE0E7FF), borderRadius: BorderRadius.circular(8)),
                        child: const Icon(Icons.add_box_outlined, color: Color(0xFF4F46E5)),
                      ),
                      const SizedBox(width: 16),
                      const Expanded(child: Text('Nurse Portal', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500))),
                      const Icon(Icons.chevron_right, color: Color(0xFF9CA3AF)),
                    ],
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Doctor Portal
              InkWell(
                onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const DoctorPortalScreen())),
                borderRadius: BorderRadius.circular(12),
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFFE5E7EB)),
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(color: const Color(0xFFFCE7F3), borderRadius: BorderRadius.circular(8)),
                        child: const Icon(Icons.local_hospital, color: Color(0xFFDB2777)),
                      ),
                      const SizedBox(width: 16),
                      const Expanded(child: Text('Doctor Portal', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500))),
                      const Icon(Icons.chevron_right, color: Color(0xFF9CA3AF)),
                    ],
                  ),
                ),
              ),
              
              const Spacer(),
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.lock_outline, size: 14, color: Color(0xFF9CA3AF)),
                  SizedBox(width: 8),
                  Text('Secure encrypted connection', style: TextStyle(color: Color(0xFF9CA3AF), fontSize: 12)),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
