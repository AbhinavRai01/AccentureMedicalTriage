import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../../config.dart';
import 'scanner_screen.dart';

class NursePortalScreen extends StatefulWidget {
  const NursePortalScreen({super.key});

  @override
  State<NursePortalScreen> createState() => _NursePortalScreenState();
}

class _NursePortalScreenState extends State<NursePortalScreen> {
  String score = 'Pending Calculation...';
  bool isLoading = false;
  
  final patientIdCtrl = TextEditingController();
  final ageCtrl = TextEditingController();
  final heartRateCtrl = TextEditingController();
  final respRateCtrl = TextEditingController();
  final spo2Ctrl = TextEditingController();
  final sbpCtrl = TextEditingController();
  final tempCtrl = TextEditingController();
  final comorbiditiesCtrl = TextEditingController(text: '0');
  final cfsCtrl = TextEditingController(text: '1');
  bool hasPriorHistory = false;

  Future<void> calculateScore() async {
    setState(() => isLoading = true);
    try {
      final res = await http.post(
        Uri.parse('${AppConfig.apiBaseUrl}/api/triage/score'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'patient_id': patientIdCtrl.text,
          'department': 'general', // Default for now
          'age': int.tryParse(ageCtrl.text) ?? 30,
          'heart_rate': int.tryParse(heartRateCtrl.text) ?? 80,
          'resp_rate': int.tryParse(respRateCtrl.text) ?? 16,
          'spo2': int.tryParse(spo2Ctrl.text) ?? 98,
          'sbp': int.tryParse(sbpCtrl.text) ?? 120,
          'temp_c': double.tryParse(tempCtrl.text) ?? 37.0,
          'has_prior_history': hasPriorHistory ? 1 : 0,
          'comorbidity_count': int.tryParse(comorbiditiesCtrl.text) ?? 0,
          'cfs_frailty_score': int.tryParse(cfsCtrl.text) ?? 1,
        }),
      );
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        final result = data['data'];
        setState(() {
           if (data['fallback'] == true) {
             score = 'Deterministic Fallback: ${result['score']}\nFlags: ${result['flags'].join(", ")}';
           } else {
             score = 'AI Triage: ${result['ai_recommendation']}\nProbability: ${result['risk_probability']} \nConfidence: ${result['confidence_score']}%';
           }
        });
      } else {
        setState(() => score = 'Error calculating score');
      }
    } catch (e) {
      setState(() => score = 'Connection Error: $e');
    } finally {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF7F9FC),
      appBar: AppBar(
        title: const Text('Nurse Portal - Triage', style: TextStyle(color: Color(0xFF191C1E), fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF191C1E)),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Patient Identification', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF191C1E))),
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE5E7EB)),
                ),
                child: TextField(
                  controller: patientIdCtrl,
                  decoration: InputDecoration(
                    labelText: 'Patient ID (e.g. P001)',
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    suffixIcon: Container(
                      margin: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFE0E7FF),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: IconButton(
                        icon: const Icon(Icons.qr_code_scanner, color: Color(0xFF4F46E5)),
                        onPressed: () async {
                          final result = await Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => const ScannerScreen()),
                          );
                          if (result != null) {
                            setState(() {
                              patientIdCtrl.text = result as String;
                            });
                          }
                        },
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              const Text('Vitals & Clinical Data', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF191C1E))),
              const SizedBox(height: 12),
              
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE5E7EB)),
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Expanded(child: _buildTextField(ageCtrl, 'Age')),
                        const SizedBox(width: 12),
                        Expanded(child: _buildTextField(heartRateCtrl, 'HR (bpm)')),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(child: _buildTextField(respRateCtrl, 'RR (/min)')),
                        const SizedBox(width: 12),
                        Expanded(child: _buildTextField(spo2Ctrl, 'SpO2 (%)')),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(child: _buildTextField(sbpCtrl, 'SBP (mmHg)')),
                        const SizedBox(width: 12),
                        Expanded(child: _buildTextField(tempCtrl, 'Temp (°C)')),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(child: _buildTextField(comorbiditiesCtrl, 'Comorbidities')),
                        const SizedBox(width: 12),
                        Expanded(child: _buildTextField(cfsCtrl, 'CFS (1-9)')),
                      ],
                    ),
                    const SizedBox(height: 12),
                    SwitchListTile(
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Prior ER Visits', style: TextStyle(fontWeight: FontWeight.w500)),
                      activeColor: const Color(0xFF006B4D),
                      value: hasPriorHistory,
                      onChanged: (val) => setState(() => hasPriorHistory = val),
                    ),
                  ],
                ),
              ),
              
              const SizedBox(height: 24),
              if (score != 'Pending Calculation...')
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFECFDF5),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: const Color(0xFF34D399)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.assessment, color: Color(0xFF059669), size: 32),
                      const SizedBox(width: 16),
                      Expanded(child: Text(score, style: const TextStyle(color: Color(0xFF065F46), fontWeight: FontWeight.bold))),
                    ],
                  ),
                ),
              
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: isLoading ? null : calculateScore,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF006B4D),
                  minimumSize: const Size.fromHeight(56),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: isLoading 
                  ? const CircularProgressIndicator(color: Colors.white) 
                  : const Text('Submit Vitals & Route Patient', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String label) {
    return TextField(
      controller: controller,
      keyboardType: TextInputType.number,
      decoration: InputDecoration(
        labelText: label,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        isDense: true,
      ),
    );
  }
}
