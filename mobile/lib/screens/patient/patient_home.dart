import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:qr_flutter/qr_flutter.dart';
import '../../config.dart';
import 'registration_screen.dart';

class PatientHomeScreen extends StatefulWidget {
  final Map<String, dynamic> accountData;
  const PatientHomeScreen({super.key, required this.accountData});

  @override
  State<PatientHomeScreen> createState() => _PatientHomeScreenState();
}

class _PatientHomeScreenState extends State<PatientHomeScreen> {
  String? selectedDependent;
  Map<String, String> dependents = {};

  Map<String, dynamic>? patientData;
  bool isLoading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    // Parse dependents from accountData
    final patients = widget.accountData['patients'] as List<dynamic>? ?? [];
    for (var p in patients) {
      dependents[p['patient_id']] = '${p['name']}';
    }
    
    if (dependents.isNotEmpty) {
      selectedDependent = dependents.keys.first;
      _fetchHistory(selectedDependent!);
    } else {
      isLoading = false;
      error = 'No patients registered to this account yet. Please register a patient first.';
    }
  }

  Future<void> _refreshAccount() async {
    try {
      final res = await http.get(Uri.parse('${AppConfig.apiBaseUrl}/api/auth/account/${widget.accountData['account_id']}'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body)['data'];
        final patients = data['patients'] as List<dynamic>? ?? [];
        setState(() {
          dependents.clear();
          for (var p in patients) {
            dependents[p['patient_id']] = '${p['name']}';
          }
          if (dependents.isNotEmpty) {
            selectedDependent = dependents.keys.first;
            error = null;
            _fetchHistory(selectedDependent!);
          }
        });
      }
    } catch(e) {}
  }

  Future<void> _fetchHistory(String patientId) async {
    setState(() {
      isLoading = true;
      error = null;
    });
    try {
      final res = await http.get(Uri.parse('${AppConfig.apiBaseUrl}/api/patient/$patientId/history'));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          patientData = data['data'];
          isLoading = false;
        });
      } else {
        setState(() {
          error = 'Failed to load history';
          isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Connection Error: $e';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Row(
          children: [
            Icon(Icons.medical_services, color: Color(0xFF006B4D)),
            SizedBox(width: 8),
            Text('Dashboard', style: TextStyle(color: Color(0xFF006B4D), fontWeight: FontWeight.bold)),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none, color: Colors.black),
            onPressed: () {},
          ),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 16.0),
            child: CircleAvatar(
              backgroundColor: Color(0xFFD1D5DB),
              child: Icon(Icons.person, color: Colors.white),
            ),
          )
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Error banner if any
            if (error != null)
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(12),
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: const Color(0xFFFEE2E2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: Color(0xFFB91C1C)),
                    const SizedBox(width: 8),
                    Expanded(child: Text(error!, style: const TextStyle(color: Color(0xFFB91C1C)))),
                    TextButton(onPressed: _refreshAccount, child: const Text('Retry', style: TextStyle(color: Color(0xFFB91C1C)))),
                  ],
                ),
              ),

            // Profile Dropdown Header
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE5E7EB)),
              ),
              child: Row(
                children: [
                  const CircleAvatar(
                    backgroundColor: Color(0xFFDBEAFE),
                    child: Icon(Icons.person, color: Color(0xFF2563EB)),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (dependents.isEmpty)
                          const Text('No Profiles', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold))
                        else
                          DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                              value: selectedDependent,
                              isDense: true,
                              icon: const Icon(Icons.keyboard_arrow_down, color: Color(0xFF6B7280)),
                              items: dependents.entries.map((entry) {
                                return DropdownMenuItem<String>(
                                  value: entry.key,
                                  child: Text(entry.value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                                );
                              }).toList(),
                              onChanged: (String? newValue) {
                                if (newValue != null && newValue != selectedDependent) {
                                  setState(() {
                                    selectedDependent = newValue;
                                  });
                                  _fetchHistory(newValue);
                                }
                              },
                            ),
                          ),
                        const Text('Primary Profile', style: TextStyle(color: Color(0xFF6B7280), fontSize: 14)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.person_add_alt_1, color: Color(0xFF6B7280)),
                    onPressed: () async {
                      await Navigator.push(context, MaterialPageRoute(
                        builder: (_) => RegistrationScreen(accountId: widget.accountData['account_id'])
                      ));
                      _refreshAccount();
                    },
                  )
                ],
              ),
            ),
            const SizedBox(height: 24),
            
            // QR Code Box
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 32),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.02), blurRadius: 10, offset: const Offset(0, 4)),
                ],
              ),
              child: Column(
                children: [
                  if (selectedDependent != null)
                    Container(
                      padding: const EdgeInsets.all(16),
                      color: const Color(0xFFF9FAFB),
                      child: QrImageView(
                        data: selectedDependent!,
                        version: QrVersions.auto,
                        size: 180.0,
                      ),
                    )
                  else
                    Container(
                      height: 180,
                      width: 180,
                      color: const Color(0xFFF9FAFB),
                      child: const Center(child: Icon(Icons.qr_code, size: 64, color: Color(0xFFD1D5DB))),
                    ),
                  
                  const SizedBox(height: 24),
                  const Text('Patient ID Ready', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Text('Scan at intake to load history\nimmediately.', textAlign: TextAlign.center, style: TextStyle(color: Color(0xFF6B7280))),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Current Status
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFE5E7EB)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Current Status', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFFECFDF5),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.circle, size: 8, color: Color(0xFF059669)),
                        SizedBox(width: 6),
                        Text('Awaiting Triage', style: TextStyle(color: Color(0xFF059669), fontWeight: FontWeight.bold, fontSize: 12)),
                      ],
                    ),
                  )
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            const Text('Activity History', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            
            // Timeline
            if (isLoading)
              const Center(child: CircularProgressIndicator())
            else if (patientData != null && patientData!['medical_events'] != null)
              ...((patientData!['medical_events'] as List).map((event) => Container(
                margin: const EdgeInsets.only(bottom: 16),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Column(
                      children: [
                        const Icon(Icons.circle, size: 12, color: Color(0xFF006B4D)),
                        Container(width: 2, height: 80, color: const Color(0xFFE5E7EB)),
                      ],
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFFE5E7EB)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(event['type'] ?? 'Event', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                Text(event['event_date'] ?? '', style: const TextStyle(color: Color(0xFF6B7280), fontSize: 14)),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(event['description'] ?? '', style: const TextStyle(color: Color(0xFF4A4A4A))),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ))),
              
            const SizedBox(height: 80), // padding for floating button
          ],
        ),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16.0),
        child: SizedBox(
          width: double.infinity,
          height: 56,
          child: ElevatedButton.icon(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFBE123C),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            icon: const Icon(Icons.warning_amber_rounded, color: Colors.white),
            label: const Text('Pre-Alert Referral', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
          ),
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF006B4D),
        unselectedItemColor: const Color(0xFF6B7280),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), label: 'Dashboard'),
          BottomNavigationBarItem(icon: Icon(Icons.people_outline), label: 'Patients'),
          BottomNavigationBarItem(icon: Icon(Icons.notifications_outlined), label: 'Alerts'),
          BottomNavigationBarItem(icon: Icon(Icons.settings_outlined), label: 'Settings'),
        ],
      ),
    );
  }
}
